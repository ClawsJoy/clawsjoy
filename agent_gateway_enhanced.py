#!/usr/bin/env python3
"""ClawsJoy Gateway v6.0 - 精简路由层

设计原则:
- 只做路由、鉴权、限流、日志
- 所有业务逻辑委托给 AgentCortex / lib
- 单一入口: /v5/execute
"""
import yaml
import json
import uuid
import os
import logging
from datetime import datetime
from pathlib import Path

import psutil
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS

# ========== Ollama 自动启动 ==========
import subprocess as _sp, time as _time, requests as _req

def _ensure_ollama():
    """确保 Ollama 双实例运行"""
    try:
        _req.get('http://127.0.0.1:11434/api/tags', timeout=3)
    except:
        print("启动 Ollama GPU 实例...")
        _sp.Popen(['ollama', 'serve'], stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
        _time.sleep(3)
    
    try:
        _req.get('http://127.0.0.1:11435/api/tags', timeout=3)
    except:
        print("启动 Ollama CPU 实例...")
        import os
        env = os.environ.copy()
        env['OLLAMA_HOST'] = '127.0.0.1:11435'
        env['OLLAMA_NUM_GPU'] = '0'
        _sp.Popen(['ollama', 'serve'], env=env, stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
        _time.sleep(5)

_ensure_ollama()

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
    # v8 记账钩子
    try:
        from core.lib.v8.billing_hook import record_if_roster_member
        server_id = data.get("server_id", "default")
        agent_name = result.get("agents_used", [""])[0] if result.get("agents_used") else ""
        tokens = result.get("tokens", 0)
        model = result.get("model", "")
        if agent_name and tokens:
            record_if_roster_member(server_id, agent_name, tokens, model)
    except:
        pass

    return jsonify(result)


@app.route("/api/v5/wisdom/chat", methods=["POST"])
def wisdom_chat():
    """兼容旧入口 → 转发到 /v5/execute"""
    return v5_execute()


@app.route("/api/v5/enhanced/chat", methods=["POST"])
def enhanced_chat():
    """[兼容旧版] 转发到统一入口"""
    return v5_execute()


@app.route("/api/agent/<agent_name>/message", methods=["POST"])
def agent_message(agent_name):
    """[兼容旧版] 旧Agent直调 → 转发到统一入口"""
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

@app.route("/")
def index():
    return jsonify({"service": "ClawsJoy Gateway", "version": "6.0.0"})

# ========== v8 API：AI劳动力管理 ==========
from core.lib.v8.roster_engine import roster_engine

@app.route("/v8/roster/list")
def v8_roster_list():
    server_id = request.args.get("server_id", "default")
    return jsonify(roster_engine.list(server_id))

@app.route("/v8/roster/hire", methods=["POST"])
def v8_roster_hire():
    data = request.json or {}
    server_id = data.get("server_id", "default")
    name = data.get("name", "")
    position_id = data.get("position", "")
    model = data.get("model", "")
    budget = data.get("budget", 0)
    try:
        with open(f"config/v8/positions/{position_id}.yaml") as f:
            pos = yaml.safe_load(f)
        if model:
            pos["model"] = model
        if budget:
            pos["budget"] = float(budget)
        result = roster_engine.hire(server_id, name, pos)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/v8/roster/fire", methods=["POST"])
def v8_roster_fire():
    data = request.json or {}
    result = roster_engine.fire(data.get("server_id", "default"), data.get("name", ""))
    return jsonify(result)

@app.route("/v8/roster/pause", methods=["POST"])
def v8_roster_pause():
    data = request.json or {}
    result = roster_engine.pause(data.get("server_id", "default"), data.get("name", ""))
    return jsonify(result)

@app.route("/v8/roster/resume", methods=["POST"])
def v8_roster_resume():
    data = request.json or {}
    result = roster_engine.resume(data.get("server_id", "default"), data.get("name", ""))
    return jsonify(result)

@app.route("/v8/roster/permissions", methods=["POST"])
def v8_roster_permissions():
    data = request.json or {}
    result = roster_engine.update_permissions(
        data.get("server_id", "default"), data.get("name", ""), data.get("permissions", {})
    )
    return jsonify(result)

@app.route("/v8/roster/budget", methods=["POST"])
def v8_roster_budget():
    data = request.json or {}
    result = roster_engine.update_budget(
        data.get("server_id", "default"), data.get("name", ""), float(data.get("budget", 0))
    )
    return jsonify(result)

@app.route("/v8/positions/list")
def v8_positions_list():
    positions = []
    pos_dir = Path("config/v8/positions")
    for f in pos_dir.glob("*.yaml"):
        with open(f) as fp:
            pos = yaml.safe_load(fp)
            pos["id"] = f.stem
            positions.append(pos)
    return jsonify(positions)

@app.route("/v8/billing/realtime")
def v8_billing_realtime():
    server_id = request.args.get("server_id", "default")
    members = roster_engine.list(server_id)
    billing = []
    total = 0
    for m in members:
        billing.append({
            "name": m["name"],
            "position": m["position"],
            "spent": m.get("spent", 0),
            "budget": m.get("budget", 0),
            "task_count": m.get("task_count", 0),
            "status": m["status"],
        })
        total += m.get("spent", 0)
    return jsonify({"total": round(total, 4), "members": billing})

# ========== v8 Ledger API ==========
from core.lib.v8.ledger import ledger

@app.route("/v8/ledger/billing")
def v8_ledger_billing():
    server_id = request.args.get("server_id", "default")
    month = request.args.get("month", None)
    return jsonify(ledger.get_billing(server_id, month))

@app.route("/v8/ledger/timeline")
def v8_ledger_timeline():
    server_id = request.args.get("server_id", "default")
    limit = int(request.args.get("limit", 30))
    return jsonify(ledger.get_timeline(server_id, limit))

# ========== v8 Task API ==========
from core.lib.v8.task_engine import task_engine

@app.route("/v8/task/create", methods=["POST"])
def v8_task_create():
    data = request.json or {}
    result = task_engine.create(
        server_id=data.get("server_id", "default"),
        title=data.get("title", ""),
        assigned_to=data.get("assigned_to", ""),
        assigned_position=data.get("assigned_position", ""),
        created_by=data.get("created_by", "老板"),
    )
    return jsonify(result)

@app.route("/v8/task/transition", methods=["POST"])
def v8_task_transition():
    data = request.json or {}
    result = task_engine.transition(
        server_id=data.get("server_id", "default"),
        task_id=data.get("task_id", ""),
        new_state=data.get("new_state", ""),
        comment=data.get("comment", ""),
    )
    return jsonify(result)

@app.route("/v8/task/list")
def v8_task_list():
    server_id = request.args.get("server_id", "default")
    status = request.args.get("status", None)
    return jsonify(task_engine.list(server_id, status))


# ========== v8 任务状态变更钩子 ==========
from core.lib.v8.task_engine import task_engine as _task_engine

def _auto_review(task_id, task_data):
    """自动调 Agent 做代码审查"""
    try:
        from core.lib.v8.roster_engine import roster_engine

        # 找 CEO
        ceo_name = "决策者"
        for m in roster_engine.list_active("default"):
            if m.get("role") == "ceo" or "决策" in m.get("name", ""):
                ceo_name = m["name"]
                break

        # 从岗位 YAML 取审查 prompt
        review_prompt = "审查以下任务，直接给出意见："
        assigned = task_data.get("assigned_to", "")
        member = roster_engine.get("default", assigned)
        if member:
            review_prompt = member.get("review_prompt", review_prompt)

        from core.agents.wisdom.wisdom_factory import wisdom_factory
        agent = wisdom_factory.get_agent("chat_agent", "workbench")
        prompt = f"{review_prompt}\n\n{task_data['title']}"
        result = agent.process(prompt)
        review_text = result.get("response", "")[:500]

        import requests as _r
        _r.post("http://localhost:5002/v8/discord/notify",
                json={
                    "channel_id": "1103302124261085338",
                    "message": f"🤖 **{ceo_name}**: {review_text}",
                    "username": ceo_name,
                },
                timeout=10)

        if "通过" in review_text or "没有问题" in review_text:
            _task_engine.transition("default", task_id, "reviewed", "审查通过")
        else:
            print(f"[v8审查] {ceo_name}: 发现问题，需修改")
    except Exception as e:
        print(f"[v8审查] 审查失败: {e}")

def _on_task_state_change(task_id, old_state, new_state, task_data):
    """状态变更时，按岗位分工让对应 Agent 发言"""
    executor = task_data.get("assigned_to", "")
    position = task_data.get("assigned_position", "")
    title = task_data.get("title", "")

    # 执行者发言
    if new_state == "running":
        _say(executor, f"收到，开始执行「{title}」")

    elif new_state == "done":
        _say(executor, f"「{title}」已完成，请审查")
        # 通知 CEO 审查
        ceo = _find_ceo()
        if ceo:
            _say(ceo, f"收到，审查「{title}」...")
            _auto_review(task_id, task_data)

    elif new_state == "reviewed":
        _say(executor, f"「{title}」审查通过")

    elif new_state == "failed":
        _say("老板", f"「{title}」执行失败，请人工处理")


def _say(who, message):
    """Agent 在频道里发言"""
    try:
        import requests as _r
        _r.post("http://localhost:5002/v8/discord/notify",
                json={
                    "channel_id": "1103302124261085338",
                    "message": f"🤖 **{who}**: {message}",
                    "username": who,
                },
                timeout=5)
    except Exception as e:
        print(f"[v8] 发言失败: {e}")


def _find_ceo():
    """从花名册找 CEO"""
    try:
        from core.lib.v8.roster_engine import roster_engine
        for m in roster_engine.list_active("default"):
            if m.get("role") == "ceo" or "决策" in m.get("name", ""):
                return m["name"]
    except:
        pass
    return None


_task_engine.on_state_change(_on_task_state_change)


@app.route("/v8/discord/notify", methods=["POST"])
def v8_discord_notify():
    """接收内部通知，通过 Webhook 转发到 Discord（支持多身份）"""
    data = request.json or {}
    channel_id = data.get("channel_id", "")
    content = data.get("message", "")
    username = data.get("username", "")
    avatar_url = data.get("avatar_url", "")

    if not channel_id or not content:
        return jsonify({"success": False})

    import requests as _r
    payload = {"content": content}
    if username:
        payload["username"] = username
    if avatar_url:
        payload["avatar_url"] = avatar_url

    r = _r.post("https://discord.com/api/webhooks/1521526206518792482/B0kL_EdzmGFoaq6nuRTx-kVPjKB9AF4yBpBUgXl0nvFiSepXUNHpT7WF1kpy23zC8fQt",
                json=payload, timeout=10)
    return jsonify({"success": r.status_code == 204})


# ====================================================================
#  启动
# ====================================================================

if __name__ == "__main__":
    from core.lib.hook_manager import HookManager
    from core.lib.startup import startup_manager
    HookManager()
    startup_manager.start()
    port = unified_config.get("services.gateway.port", 5002)
    print(f"🚀 ClawsJoy Gateway v6.0 启动在端口 {port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
