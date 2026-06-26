#!/usr/bin/env python3
"""ClawsJoy Gateway v6.0 - 精简路由层

设计原则:
- 只做路由、鉴权、限流、日志
- 所有业务逻辑委托给 AgentCortex / lib
- 单一入口: /v5/execute
"""

import json
import uuid
import os
import logging
from datetime import datetime
from pathlib import Path

import psutil
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS

# ========== 核心入口 ==========
from core.agents.cortex import agent_cortex
from core.lib.llm_client import llm_client

# ========== 中间件 ==========
from core.lib.auth_middleware import require_auth
from core.lib.error_handler import register_error_handlers
from core.lib.performance_middleware import get_perf_stats
from core.lib.rate_limiter import rate_limit, rate_limiter
from core.lib.response_cache import response_cache
from core.lib.unified_config import unified_config
from core.lib.safety_guard import set_safe_recursion_limit

# ========== 蓝图 ==========
from api.v5 import agents, butler, health
from routes.director_canvas_routes import canvas_bp

set_safe_recursion_limit()

# ========== 日志 ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/gateway.log"), logging.StreamHandler()],
)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# ========== Flask ==========
app = Flask(__name__)
register_error_handlers(app)
CORS(app)

app.register_blueprint(agents.api_bp, url_prefix="/api/v5")
app.register_blueprint(health.api_bp, url_prefix="/api/v5")
app.register_blueprint(butler.api_bp, url_prefix="/api/v5")
app.register_blueprint(canvas_bp)

# ========== Prometheus（可选） ==========
try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
    request_count = Counter("clawsjoy_requests_total", "Total requests", ["method", "endpoint", "status"])
    request_duration = Histogram("clawsjoy_request_duration_seconds", "Request duration", ["method", "endpoint"])
except ImportError:
    CONTENT_TYPE_LATEST = "text/plain"
    def generate_latest(): return ""
    request_count = request_duration = None

# ========== Swagger ==========
from flasgger import Swagger
swagger = Swagger(app, config={
    "headers": [],
    "specs": [{"endpoint": "apispec", "route": "/apispec.json"}],
    "swagger_ui": True,
    "specs_route": "/apidocs/",
})


# ====================================================================
#  核心路由（唯一入口）
# ====================================================================

@app.route("/v5/execute", methods=["POST"])
def v5_execute():
    """统一执行入口 - 所有Agent调用走这里"""
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "无效JSON"}), 400

    raw_input = data.get("raw_input") or data.get("message") or ""
    if not raw_input:
        return jsonify({"error": "raw_input或message必填"}), 400

    user_id = data.get("user_id", "guest")
    session_id = data.get("session_id")
    context = {"session_id": session_id} if session_id else None

    result = agent_cortex.process(raw_input, user_id, context)
    return jsonify(result)


@app.route("/api/v5/wisdom/chat", methods=["POST"])
def wisdom_chat():
    """兼容旧入口 → 转发到 /v5/execute"""
    return v5_execute()


@app.route("/api/v5/enhanced/chat", methods=["POST"])
def enhanced_chat():
    """[DEPRECATED] → 转发到统一入口"""
    return v5_execute()


@app.route("/api/agent/<agent_name>/message", methods=["POST"])
def agent_message(agent_name):
    """[DEPRECATED] 旧Agent直调 → 转发到统一入口"""
    return v5_execute()


# ====================================================================
#  基础路由
# ====================================================================

@app.route("/health", methods=["GET"])
def health():
    from core.lib.startup import startup_manager
    from core.lib.hardware_probe import hardware_probe
    return jsonify({
        "status": "healthy" if startup_manager.ready else "starting",
        "version": "6.0.0",
        "startup": startup_manager.status(),
        "hardware": hardware_probe.report(),
    })

@app.route("/metrics", methods=["GET"])
def metrics():
    if "prometheus" in request.headers.get("Accept", ""):
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
    return jsonify({
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage("/").percent,
        },
        "status": "ok",
    })

@app.route("/api/endpoints", methods=["GET"])
def list_endpoints():
    endpoints = [{"path": rule.rule, "methods": list(rule.methods)}
                 for rule in app.url_map.iter_rules() if not rule.rule.startswith("/static")]
    return jsonify({"endpoints": endpoints, "total": len(endpoints)})


# ====================================================================
#  会话
# ====================================================================

from core.lib.session_manager import session_manager

@app.route("/api/v5/session/create", methods=["POST"])
def session_create():
    data = request.json or {}
    user_id = data.get("user_id", "default")
    session_id = str(uuid.uuid4())[:8]
    session_manager.get_or_create(session_id, user_id)
    return jsonify({"success": True, "session_id": session_id})

@app.route("/api/v5/session/list", methods=["GET"])
def session_list():
    user_id = request.args.get("user_id", "default")
    return jsonify({"success": True, "sessions": session_manager.list_sessions(user_id)})


# ====================================================================
#  记忆（委托给 memory_agent）
# ====================================================================

@app.route("/api/v5/memory/remember", methods=["POST"])
def memory_remember():
    data = request.json or {}
    user_id = data.get("user_id", "guest")
    fact = data.get("fact", "")
    # 优先用MemoryAgent，降级到文件存储
    from core.lib.gateway_helpers import save_memory
    result = agent_cortex.process(f"记住 {fact}", user_id)
    if result.get("success"):
        return jsonify({"success": True, "message": "记忆已存储"})
    save_memory(user_id, fact)
    return jsonify({"success": True, "message": "记忆已存储"})

@app.route("/api/v5/memory/recall", methods=["POST"])
def memory_recall():
    data = request.json or {}
    user_id = data.get("user_id", "guest")
    query = data.get("query", "")
    result = agent_cortex.process(f"回忆 {query}", user_id)
    return jsonify({"success": True, "results": [result.get("response", "")]})

@app.route("/api/v5/memory/stats", methods=["GET"])
def memory_stats():
    user_id = request.args.get("user_id", "guest")
    result = agent_cortex.process("列出所有记忆", user_id)
    return jsonify({"success": True, "total": len(result.get("response", ""))})


# ====================================================================
#  统计与监控
# ====================================================================

@app.route("/api/v5/stats/cache", methods=["GET"])
def cache_stats():
    return jsonify(response_cache.get_stats())

@app.route("/api/v5/stats/performance", methods=["GET"])
def performance_stats():
    return jsonify(get_perf_stats())

@app.route("/api/v5/stats/ratelimit", methods=["GET"])
def ratelimit_stats():
    return jsonify(rate_limiter.get_stats(request.args.get("user_id")))

@app.route("/api/v5/health/detailed", methods=["GET"])
def detailed_health():
    from core.lib.health_check import health_checker
    return jsonify(health_checker.check_all())


# ====================================================================
#  Agent管理
# ====================================================================

@app.route("/api/v5/agent/list", methods=["GET"])
def agent_list():
    from core.lib.agent_registry import agent_registry
    return jsonify({"success": True, "agents": agent_registry.list_all()})

@app.route("/api/v5/agent/broadcast", methods=["POST"])
def agent_broadcast():
    """广播 → 通过AgentCortex逐Agent调用"""
    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")

    from core.lib.agent_registry import agent_registry
    agent_names = agent_registry.list_agent_names()
    results = []
    for name in agent_names[:16]:
        r = agent_cortex.process(f"[广播] {message}", user_id)
        results.append({"agent": name, "success": r.get("success", False)})

    return jsonify({"success": True, "results": results})


# ====================================================================
#  技能
# ====================================================================

@app.route("/api/skills/list", methods=["GET"])
def list_skills():
    from core.lib.unified_skill_manager import unified_manager
    return jsonify({"success": True, "skills": unified_manager.list_all()})

@app.route("/api/skills/execute", methods=["POST"])
def execute_skill():
    from core.lib.skill_loader_v3 import skill_loader
    data = request.json or {}
    result = skill_loader.execute(data.get("skill", ""), data.get("params", {}))
    return jsonify({"success": True, "result": result})


# ====================================================================
#  用户认证
# ====================================================================

from core.lib.auth_api import AuthManager
auth_manager = AuthManager()

@app.route("/api/user/register", methods=["POST"])
def user_register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    if not username or not password:
        return jsonify({"success": False, "error": "用户名和密码不能为空"}), 400
    result = auth_manager.register(username, password, role="user")
    if result.get("success"):
        from core.lib.gateway_helpers import create_user_directories
        create_user_directories(username, result["user_id"])
    return jsonify(result)

@app.route("/api/user/login", methods=["POST"])
def user_login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    if not username or not password:
        return jsonify({"success": False, "error": "用户名和密码不能为空"}), 400
    auth = AuthManager()
    if username not in auth.users:
        return jsonify({"success": False, "error": "用户不存在"}), 401
    user = auth.users[username]
    if user["password_hash"] != auth._hash_password(password):
        return jsonify({"success": False, "error": "密码错误"}), 401
    token = auth._generate_token(user["user_id"], username, user.get("role", "user"))
    user["last_login"] = datetime.now().isoformat()
    auth._save_users()
    return jsonify({"success": True, "token": token, "user_id": user["user_id"],
                    "username": username, "role": user.get("role", "user")})




# ====================================================================
#  文件与项目
# ====================================================================

@app.route("/api/v5/project/list", methods=["GET"])
def project_list():
    from core.lib.code_repo import get_code_repo
    return jsonify({"success": True, "projects": get_code_repo(
        request.args.get("user_id", "codex_user")).list_projects()})


# ====================================================================
#  流式输出（SSE）
# ====================================================================

@app.route("/api/v5/chat/stream", methods=["POST"])
def chat_stream():
    from flask import Response, stream_with_context
    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")

    def generate():
        result = agent_cortex.process(message, user_id)
        response_text = result.get("response", "")
        for i in range(0, len(response_text), 20):
            chunk = response_text[i:i+20]
            yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


# ====================================================================
#  反馈
# ====================================================================

@app.route("/api/v5/feedback", methods=["POST"])
def submit_feedback():
    data = request.json or {}
    feedback_file = Path("data/feedback.json")
    existing = json.loads(feedback_file.read_text()) if feedback_file.exists() else {"success": [], "failure": []}
    cat = "success" if data.get("rating", 0) >= 4 else "failure"
    existing[cat].append({"user_id": data.get("user_id", "anon"), "feedback": data.get("feedback", ""),
                          "rating": data.get("rating", 0), "timestamp": datetime.now().isoformat()})
    for c in ["success", "failure"]:
        existing[c] = existing[c][-1000:]
    feedback_file.write_text(json.dumps(existing, indent=2))
    return jsonify({"success": True})


# ====================================================================
#  静态文件
# ====================================================================

@app.route('/web/<path:filename>')
def serve_web(filename):
    return send_from_directory('web', filename)

@app.route('/exports/<path:filename>')
def serve_exports(filename):
    return send_from_directory('exports', filename)

@app.route('/api/export/comic/<project>')
def export_comic(project):
    import subprocess, os
    script = "scripts/export_for_seedance.py"
    if not os.path.exists(script):
        return {"success": False, "error": "导出脚本不存在"}
    result = subprocess.run(["python3", script], capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        return {"success": True, "download_url": f"/exports/seedance_{project}.zip"}
    return {"success": False, "error": result.stderr[:200]}

@app.route('/workbench')
def workbench():
    return send_from_directory('web/dashboard', 'workbench.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('web/dashboard', 'index.html')

@app.route('/web')
def web_index():
    return send_from_directory('web', 'index.html')

for panel in ["code_agent_panel", "writer_panel", "director_panel",
              "preview", "tab_editor", "debug_console", "diff_viewer",
              "workflow_panel", "butler_3d"]:
    app.add_url_rule(f"/{panel}.html", panel.replace("_panel", "_page") if "panel" in panel else panel,
                     lambda p=panel: send_from_directory("templates", f"{p}.html"))


# ====================================================================
#  启动
# ====================================================================

@app.route("/")
def index():
    return jsonify({"service": "ClawsJoy Gateway", "version": "6.0.0"})

if __name__ == "__main__":
    from core.lib.hook_manager import HookManager
    from core.lib.startup import startup_manager
    HookManager()
    startup_manager.start()
    port = unified_config.get("services.gateway.port", 5002)
    print(f"🚀 ClawsJoy Gateway v6.0 启动在端口 {port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
