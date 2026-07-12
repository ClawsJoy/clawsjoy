#!/usr/bin/env python3
"""ClawsJoy Gateway v6.0 - 精简路由层

设计原则:
- 只做路由、鉴权、限流、日志
- 所有业务逻辑委托给 AgentCortex / lib
- 单一入口: /v5/execute
"""

import os

from dotenv import load_dotenv
load_dotenv("/home/flybo/clawsjoy_v5/config/.env", override=True)

# 如果 .env 文件没有配置代理，清除 shell 残留的代理
_env_has_proxy = False
with open("/home/flybo/clawsjoy_v5/config/.env") as _f:
    for _line in _f:
        if _line.startswith("HTTP_PROXY=") or _line.startswith("HTTPS_PROXY="):
            _env_has_proxy = True
            break
if not _env_has_proxy:
    for _k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"]:
        os.environ.pop(_k, None)
import os as _os_check
_DEEPSEEK_KEY_LOADED = _os_check.environ.get("DEEPSEEK_API_KEY", "NOT_FOUND")

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
    channel_id = data.get("channel_id", "")
    
    # ✅ 修复：一次性构建 context，包含 channel_id
    context = {}
    if session_id:
        context["session_id"] = session_id
    if channel_id:
        context["channel_id"] = channel_id
    context = context if context else None
    # ========== 包工头适配层 ==========
    print(f"[V5] {user_id} | {raw_input[:100]}")
    team_words = ["你们", "大家", "团队", "帮我做", "帮我写", "帮我分析", "分工"]
    action_words = ["做", "写", "分析", "准备", "规划", "设计", "制作", "拟定"]
    deliverable_words = ["方案", "报告", "计划", "文档", "视频", "宣传", "脚本", "清单"]

    has_team = any(w in raw_input for w in team_words)
    has_action = any(w in raw_input for w in action_words)
    has_deliverable = any(w in raw_input for w in deliverable_words)

    if has_team and has_action and has_deliverable:
        from core.lib.v8.task_orchestrator import orchestrator
        result = orchestrator.plan(raw_input, user_id, channel_id)
        return jsonify(result)
    # ========== 适配层结束 ==========
    # ========== 任务上下文检测 ==========
    if not (has_team and has_action and has_deliverable):
        try:
            from core.lib.v8.task_engine import task_engine
            active_tasks = task_engine.list("default")
            user_tasks = [t for t in active_tasks 
                          if t.get("created_by") == user_id 
                          and t["status"] in ("pending", "running", "done", "reviewed")]
            if user_tasks:
                status_kw = ["完成", "进度", "怎么样了", "到哪", "日志", "审查", "审核", "任务", "第几步"]
                if any(kw in raw_input for kw in status_kw):
                    by_status = {"pending": [], "running": [], "done": [], "reviewed": [], "failed": []}
                    for t in user_tasks[-8:]:
                        by_status.get(t["status"], []).append(t)
                    
                    lines = ["📊 **任务状态**\n"]
                    for s, icon in [("running", "🔄"), ("done", "✅"), ("reviewed", "✔️"), ("pending", "⏳"), ("failed", "❌")]:
                        for t in by_status[s]:
                            lines.append(f"{icon} {t['title']} → @{t.get('assigned_to', '待分配')}")
                    
                    result = {"success": True, "response": "\n".join(lines), "method": "task_status"}
                    return jsonify(result)
        except:
            pass
    # ========== 任务上下文检测结束 ==========

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

    # 逐条发送 YouTube 搜索结果到 Discord
    videos = result.get("videos", [])
    if videos and channel_id:
        import requests as _r
        for i, v in enumerate(videos):
            msg = f"**{v['title']}**\n{v['channel']} | {v['url']}"
            try:
                r = _r.post("http://localhost:5002/v8/discord/notify",
                        json={"channel_id": channel_id, "message": msg, "username": "YouTube"},
                        timeout=5)
            except Exception:
                pass

    # 发送 proactive 建议到 Discord
    proactive = result.get("proactive", "")
    if proactive and channel_id:
        try:
            import requests as _r
            _r.post("http://localhost:5002/v8/discord/notify",
                    json={"channel_id": channel_id, "message": proactive, "username": "ClawsJoy"},
                    timeout=5)
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

@app.route("/v9/task/save_progress", methods=["POST"])
def v9_save_task_progress():
    """保存任务中断进度到 .agent_state.json"""
    data = request.json or {}
    user_id = data.get("user_id", "default")
    session_id = data.get("session_id", "default")
    progress = data.get("progress", {})
    
    state_file = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev/.agent_state.json")
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    
    state["task_progress"] = {
        "status": "paused",
        "original_task": progress.get("original_task", ""),
        "completed_steps": progress.get("completed_steps", []),
        "pending_steps": progress.get("pending_steps", []),
        "total_rounds": progress.get("total_rounds", 0),
        "paused_at": datetime.now().isoformat()
    }
    
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    return jsonify({"success": True})

@app.route("/v9/task/<task_id>", methods=["GET"])
def v9_task_status(task_id):
    import json as _json
    user_id = request.args.get("user_id", "default")
    session_id = request.args.get("session_id", "default")
    
    # 优先检查异步任务状态
    async_state_file = Path(f"data/projects/{user_id}/{session_id}/.task_state.json")
    if async_state_file.exists():
        async_state = _json.loads(async_state_file.read_text())
        return jsonify({"success": True, "status": async_state.get("status", "running"), "async_task": async_state})
    
    # 回退到同步任务状态
    state_file = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev/.agent_state.json")
    if state_file.exists():
        state = _json.loads(state_file.read_text())
        tp = state.get("task_progress", {})
        return jsonify({"success": True, "status": tp.get("last_action", "running"), "task_progress": tp})
    return jsonify({"success": True, "status": "not_found"})

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
    data = request.json
    rating = data.get("rating", 0)
    question = data.get("question", "")
    answer = data.get("answer", "")
    user_id = data.get("user_id", "anon")
    intent = data.get("intent", "")
    skill = data.get("skill", "")

    # ========== 1. 原有逻辑：存入 feedback.json ==========
    feedback_file = Path("data/feedback.json")
    existing = json.loads(feedback_file.read_text()) if feedback_file.exists() else {"success": [], "failure": []}
    category = "success" if rating >= 4 else "failure"
    existing[category].append({
        "user_id": user_id,
        "question": question,
        "answer": answer[:200],
        "rating": rating,
        "timestamp": datetime.now().isoformat()
    })
    feedback_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False))

    # ========== 2. 新增：存入统一训练数据集 ==========
    train_file = Path("data/training/training_data.json")
    if train_file.exists():
        with open(train_file, "r") as f:
            train_data = json.load(f)
    else:
        train_data = []

    # 只存储高质量数据 (rating >= 4)
    if rating >= 4 and question and answer:
        train_data.append({
            "input": question,
            "output": answer,
            "rating": rating,
            "intent": intent,
            "skill": skill,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })
        with open(train_file, "w") as f:
            json.dump(train_data, f, indent=2, ensure_ascii=False)
        print(f"[Feedback] 新增训练数据: {question[:30]}... (总数: {len(train_data)})")

    # ========== 3. 新增：触发自学习 ==========
    if rating >= 4:
        try:
            from engine.evolution.self_learning import self_learning
            self_learning.learn_from_interaction(
                user_id=user_id,
                query=question,
                intent=intent,
                skill_used=skill,
                success=True,
                confidence=rating / 5.0
            )
        except Exception as e:
            print(f"[Feedback] 自学习失败: {e}")

    # ========== 4. 新增：检查是否需要触发训练 ==========
    if rating >= 4:
        try:
            from scripts.auto_train_trigger import check_and_trigger
            check_and_trigger()
        except ImportError:
            # 如果 auto_train_trigger 不存在，使用内联检查
            if len(train_data) >= 10:
                print(f"[Feedback] 训练数据达 {len(train_data)} 条，触发训练")
                import subprocess
                subprocess.Popen(
                    ["python", "scripts/train_model.py", "--quick"],
                    cwd=Path(__file__).parent
                )
        except Exception as e:
            print(f"[Feedback] 训练触发失败: {e}")

    return {"success": True}

# ====================================================================
#  静态文件
# ====================================================================

@app.route('/web/<path:filename>')
def serve_web(filename):
    return send_from_directory('web', filename)

@app.route("/v5.1")
@app.route("/v5.1/")
@app.route("/v5.1/<path:filename>")

def serve_v51(filename="index_root.html"):

    return send_from_directory("web/v5.1", filename)
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

@app.route('/favicon.ico')
def favicon():
    from flask import send_from_directory
    return send_from_directory('static', 'favicon.ico')

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
    created_by = request.args.get("created_by", None)
    tasks = task_engine.list(server_id, status)
    if created_by:
        tasks = [t for t in tasks if t.get("created_by") == created_by]
    return jsonify(tasks)



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


# 在 agent_gateway_enhanced.py 末尾加
@app.route("/v5/tts", methods=["POST"])
def tts_endpoint():
    from core.lib.voice_service import voice_service
    import base64
    data = request.json
    text = data.get("text", "")
    audio_file = voice_service.text_to_speech(text)
    if audio_file:
        with open(audio_file, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        return jsonify({"audio": audio_base64})
    return jsonify({"error": "TTS failed"}), 500


@app.route("/speech/to_text", methods=["POST"])
def speech_to_text():
    from core.lib.voice_service import voice_service
    import tempfile
    import os

    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "No audio file"}), 400

    # 保存上传的音频
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        audio_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        # 调用voice_service识别
        text = voice_service.speech_to_text(tmp_path)
        
        # 清理临时文件
        os.unlink(tmp_path)
        
        if text:
            return jsonify({"text": text})
        else:
            return jsonify({"text": "", "error": "No speech detected"}), 200
            
    except Exception as e:
        # 确保清理临时文件
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        return jsonify({"error": str(e)}), 500
# ====================================================================
#  V9 沙箱 & Agent API
# ====================================================================

from core.lib.tool_executor import tool_executor
ALLOWED_COMMANDS = ["python", "python3", "pip", "git", "grep", "cat", "ls", "pwd", "echo", "pytest", "node", "npm", "head", "tail", "wc", "find", "cd"]
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "80000"))


# 同会话文件读取缓存
_read_cache = {}
_session_artifacts = {}  # {session_key: [artifacts]}
_content_hashes = {}  # {path: hash}

# ===== V9 异步任务执行引擎 =====
import threading as _threading

def _execute_agent_task(user_id, session_id, messages, model, task_id):
    """后台执行 Agent 任务，循环处理 tool_calls 直到完成"""
    import json as _json
    from core.lib.v8.adapters.deepseek_adapter import DeepSeekAdapter
    
    state_file = Path(f"data/projects/{user_id}/{session_id}/.task_state.json")
    
    def _save_state(status, content=None, tokens=0):
        state_file.write_text(_json.dumps({
            "status": status, "content": content, "tokens": tokens,
            "updated": datetime.now().isoformat()
        }, ensure_ascii=False))
    
    import threading as _th
    print(f"[V9] thread={_th.current_thread().name}, key_in_environ={'DEEPSEEK_API_KEY' in os.environ}, key_len={len(os.environ.get('DEEPSEEK_API_KEY',''))}")
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        _save_state("failed", "未配置 API Key")
        return
    
    try:
        tools = [
            {"type": "function", "function": {"name": "read_file", "strict": True, "description": "读取文件内容，自动带行号。支持行范围和关键词搜索。cached:true表示文件已读过未变化。读取测试文件时可能返回status_hint:\"tests_found\"提示可直接验证。", "parameters": {"type": "object", "additionalProperties": False, "properties": {"path": {"type": "string", "description": "文件路径"}, "search": {"type": "string", "description": "搜索关键词，返回匹配行"}, "lines_start": {"type": "integer", "description": "起始行号"}, "lines_end": {"type": "integer", "description": "结束行号"}, "verify_line": {"type": "integer", "description": "验证指定行号"}, "verify_expected": {"type": "string", "description": "期望的内容，与指定行比对返回match"}}, "required": ["path"]}}},
            {"type": "function", "function": {"name": "write_file", "strict": True, "description": "写入文件。支持按行修改：write_file(path, line=98, content=\"新行内容\")。也支持完整写入：write_file(path, content=\"完整内容\")", "parameters": {"type": "object", "additionalProperties": False, "properties": {"path": {"type": "string"}, "content": {"type": "string"}, "line": {"type": "integer", "description": "行号，只替换该行"}}, "required": ["path"]}}},
            {"type": "function", "function": {"name": "list_dir", "strict": True, "description": "列出目录", "parameters": {"type": "object", "additionalProperties": False, "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
            {"type": "function", "function": {"name": "search_files", "strict": True, "description": "搜索文件", "parameters": {"type": "object", "additionalProperties": False, "properties": {"query": {"type": "string"}, "path": {"type": "string"}}, "required": ["query", "path"]}}},
            {"type": "function", "function": {"name": "execute_command", "strict": True, "description": "执行命令", "parameters": {"type": "object", "additionalProperties": False, "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
            {"type": "function", "function": {"name": "query_index", "strict": True, "description": "查询代码索引，返回结构化结果。用法：query_index(query='analysis_agent 有哪些方法') 或 query_index(query='谁调用了 _resp')", "parameters": {"type": "object", "additionalProperties": False, "properties": {"query": {"type": "string", "description": "自然语言查询"}}, "required": ["query"]}}},
        ]
        adapter = DeepSeekAdapter(api_key=api_key, model=model)
        max_rounds = 100
        total_tokens = 0
        
        for _round in range(max_rounds):
            resp = adapter.execute_with_tools(
                messages=messages, tools=tools, user_id=user_id,
                temperature=0.7, max_tokens=2000
            )
            
            if not resp.get("success"):
                _save_state("failed", resp.get("error", "API错误"))
                return
            
            data_resp = resp["data"]
            msg = data_resp.get("choices", [{}])[0].get("message", {})
            total_tokens += resp.get("tokens", 0)
            
            if not msg.get("tool_calls"):
                # 任务完成
                _save_state("done", msg.get("content", ""), total_tokens)
                return
            
            # 执行工具调用
            messages.append({"role": "assistant", "content": msg.get("content", ""), "tool_calls": msg["tool_calls"]})
            
            # 推送中间过程到状态文件
            if msg.get("content"):
                _save_state("running", msg["content"], total_tokens)
            for tc in msg["tool_calls"]:
                try:
                    args = _json.loads(tc["function"]["arguments"])
                    print(f"[V9 async] 执行工具: {tc['function']['name']}, args={str(args)[:100]}")
                    tool_result = _execute_sandbox_tool(tc["function"]["name"], args, user_id, session_id)
                    print(f"[V9 async] 工具返回: {str(tool_result)[:100]}")
                    # 截断 tool_result 中的 content 字段，防止 messages 膨胀
                    if isinstance(tool_result, dict) and "content" in tool_result:
                        c = tool_result["content"]
                        if isinstance(c, str) and len(c) > 2000:
                            tool_result["content"] = c[:2000] + f"\n... (内容已截断，共 {len(c)} 字符)"
                    messages.append({"role": "tool", "tool_call_id": tc["id"], "content": str(tool_result)})
                except Exception as _tool_err:
                    print(f"[V9 async] 工具执行失败: {_tool_err}")
                    _save_state("failed", f"工具执行失败: {_tool_err}")
                    return
            
            _save_state("running", None, total_tokens)
        
        _save_state("timeout", "超过最大轮次", total_tokens)
    except Exception as e:
        _save_state("failed", str(e))

def _execute_sandbox_tool(tool_name, args, user_id, session_id):
    """执行单个沙箱工具"""
    base = Path(f"data/projects/{user_id}/{session_id}")
    try:
        if tool_name == "read_file":
            path = args.get("path", "")
            target = _resolve_path(base, path)
            result = tool_executor.execute("file_tools", {"action": "read", "path": str(target)})
            _consecutive_reads += 1
            if _consecutive_reads >= 5:
                if isinstance(result, dict):
                    result["hint"] = "已经读取了多个文件，建议基于已有信息直接操作，不要继续探索"
            return result
        elif tool_name == "write_file":
            # 写文件前清理 messages 中的 read_file 残留，释放上下文
            if _consecutive_reads >= 3:
                current_path = args.get("path", "")
                for msg in messages:
                    if msg["role"] == "tool" and len(msg.get("content", "")) > 500:
                        if current_path and current_path in str(msg.get("content", "")):
                            continue
                        msg["content"] = msg["content"][:500] + f"\n... (已释放 {len(msg['content'])} 字符)"
            _consecutive_reads = 0
            target = _resolve_path(base, args.get("path", ""))
            line = args.get("line", 0)
            content_str = args.get("content", "")
            if line > 0:
                # 按行修改
                original_lines = target.read_text(encoding="utf-8").split("\n") if target.exists() else []
                if line <= len(original_lines):
                    original_lines[line - 1] = content_str
                    target.write_text("\n".join(original_lines), encoding="utf-8")
                    return {"success": True, "line": line}
                else:
                    return {"success": False, "error": f"行号 {line} 超出文件范围 (1-{len(original_lines)})"}
            else:
                # 完整写入：行数保护 + 备份
                if target.exists():
                    original = target.read_text(encoding="utf-8")
                    orig_lines = original.split("\n")
                    new_lines = content_str.split("\n")
                    if len(new_lines) < len(orig_lines) - 5:
                        return {"success": False, "error": f"完整写入模式下 content 只有 {len(new_lines)} 行，原文件有 {len(orig_lines)} 行。请改用 line 参数修改单行。"}
                    backup = target.with_suffix(target.suffix + ".bak")
                    backup.write_text(original, encoding="utf-8")
                target.write_text(content_str, encoding="utf-8")
                return {"success": True}
        elif tool_name == "list_dir":
            target = _resolve_path(base, args.get("path", "."))
            files = [p.name for p in target.iterdir() if p.is_file()][:20]
            dirs = [p.name for p in target.iterdir() if p.is_dir()]
            return {"success": True, "files": files, "dirs": dirs}
        elif tool_name == "search_files":
            import glob
            path = _resolve_path(base, args.get("path", "."))
            query = args.get("query", "*")
            results = [str(p.relative_to(base)) for p in path.rglob(query) if p.is_file()][:20]
            return {"success": True, "results": results}
        elif tool_name == "execute_command":
            cmd = args.get("command", "")
            import subprocess
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, cwd=str(base / "clawsjoy_dev"))
            return {"success": True, "stdout": result.stdout, "stderr": result.stderr}
        elif tool_name == "query_index":
            import re as _re
            import warnings
            warnings.filterwarnings("ignore", category=SyntaxWarning)
            query = args.get("query", "")
            if _code_indexer is None or not _code_indexer._keyword_index:
                return {"success": False, "error": "代码索引尚未初始化"}
            # 关键词匹配
            results = []
            query_lower = query.lower()
            for filepath, keywords in _code_indexer._keyword_index.items():
                match_score = 0
                for kw in keywords:
                    if kw.lower() in query_lower or query_lower in kw.lower():
                        match_score += 1
                if match_score > 0:
                    # 获取 AST 解析结果
                    blocks = _code_indexer.parse_file(filepath)
                    results.append({
                        "file": filepath,
                        "keywords": keywords,
                        "match_score": match_score,
                        "blocks": blocks[:20]
                    })
            results.sort(key=lambda x: x["match_score"], reverse=True)
            return {"success": True, "query": query, "results": results[:10]}
        else:
            return {"success": False, "error": f"未知工具: {tool_name}"}
        _consecutive_reads = 0
    except Exception as e:
        return {"success": False, "error": str(e)}

def _resolve_path(base, path):
    """路径解析——复用已有的逻辑"""
    path_obj = Path(path)
    if path_obj.is_absolute() or str(path).startswith("data/projects/"):
        return path_obj
    project_root = "clawsjoy_dev"
    try:
        state_file = base / "clawsjoy_dev" / ".agent_state.json"
        if state_file.exists():
            import json as _json
            project_root = _json.loads(state_file.read_text()).get("project_root", "clawsjoy_dev")
    except:
        pass
    if str(path) == project_root or str(path).startswith(f"{project_root}/"):
        return base / path
    elif str(path).startswith(".") or "/" not in str(path):
        return base / path
    return base / project_root / path
# ===== 异步引擎结束 =====
_background_tasks = {}  # {task_id: {"status": "running", "result": None, "thread": Thread}}
_code_indexer = None  # CodeIndexer 实例，异步引擎可访问
_consecutive_reads = 0  # 连续 read_file 计数器

def _get_agent_tools():
    """返回 Agent 工具定义列表。新增工具只需改此处。"""
    return [
        {"type": "function", "function": {"name": "read_file", "strict": True, "description": "读取文件内容，自动带行号。支持行范围和关键词搜索。cached:true表示文件已读过未变化。读取测试文件时可能返回status_hint:\"tests_found\"提示可直接验证。", "parameters": {"type": "object", "additionalProperties": False, "properties": {"path": {"type": "string", "description": "文件路径"}, "search": {"type": "string", "description": "搜索关键词，返回匹配行"}, "lines_start": {"type": "integer", "description": "起始行号"}, "lines_end": {"type": "integer", "description": "结束行号"}, "verify_line": {"type": "integer", "description": "验证指定行号"}, "verify_expected": {"type": "string", "description": "期望的内容，与指定行比对返回match"}}, "required": ["path"]}}},
        {"type": "function", "function": {"name": "write_file", "strict": True, "description": "写入文件。支持按行修改：write_file(path, line=98, content=\"新行内容\")。也支持完整写入：write_file(path, content=\"完整内容\")", "parameters": {"type": "object", "additionalProperties": False, "properties": {"path": {"type": "string"}, "content": {"type": "string"}, "line": {"type": "integer", "description": "行号，只替换该行"}}, "required": ["path"]}}},
        {"type": "function", "function": {"name": "list_dir", "strict": True, "description": "列出目录", "parameters": {"type": "object", "additionalProperties": False, "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
        {"type": "function", "function": {"name": "search_files", "strict": True, "description": "搜索文件", "parameters": {"type": "object", "additionalProperties": False, "properties": {"query": {"type": "string"}, "path": {"type": "string"}}, "required": ["query", "path"]}}},
        {"type": "function", "function": {"name": "execute_command", "strict": True, "description": "执行命令", "parameters": {"type": "object", "additionalProperties": False, "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
        {"type": "function", "function": {"name": "query_index", "strict": True, "description": "查询代码索引，返回结构化结果。用法：query_index(query='analysis_agent 有哪些方法') 或 query_index(query='谁调用了 _resp')", "parameters": {"type": "object", "additionalProperties": False, "properties": {"query": {"type": "string", "description": "自然语言查询"}}, "required": ["query"]}}},
    ]

@app.route("/v9/sandbox/read", methods=["POST"])
def v9_sandbox_read():
    data = request.json or {}
    user_id = data.get("user_id", "default")
    session_id = data.get("session_id", "default")
    filepath = data.get("path", "")
    if not filepath:
        return jsonify({"success": False, "error": "path 必填"})
    base = Path(f"data/projects/{user_id}/{session_id}")
    base.mkdir(parents=True, exist_ok=True)
    filepath_obj = Path(filepath)
    if filepath_obj.is_absolute() or str(filepath).startswith("data/projects/"):
        target = filepath_obj
    else:
        target = base / filepath
    if not str(target.resolve()).startswith(str(base.resolve())):
        return jsonify({"success": False, "error": "路径越权"})
    
    # artifact 采集
    _session_key = f"{user_id}/{session_id}"
    _start_time = __import__('time').time()
    
    # 先获取文件内容（缓存或磁盘）
    cache_key = str(target.resolve())
    content_str = _read_cache.get(cache_key)
    from_cache = content_str is not None
    
    if not from_cache:
        result = tool_executor.execute("file_tools", {"action": "read", "path": str(target)})
        if result.get("success"):
            content_str = result.get("content", "")
            _read_cache[cache_key] = content_str
        else:
            return jsonify(result)
    
    lines = content_str.split('\n')
    total_lines = len(lines)
    
    # search 参数
    search = data.get("search", "")
    if search:
        matched = [f"{i+1:4d}|{l}" for i, l in enumerate(lines) if search.lower() in l.lower()]
        if matched:
            return jsonify({
                "success": True, "content": '\n'.join(matched[:50]),
                "path": str(target), "lines": total_lines, "matched": len(matched), "cached": from_cache
            })
        else:
            return jsonify({
                "success": True,
                "content": f"全文搜索完成，未找到 '{search}'。文件共 {total_lines} 行。",
                "path": str(target), "lines": total_lines, "matched": 0, "cached": from_cache
            })
    
    # lines_start / lines_end 参数
    line_start = int(data.get("lines_start", 0) or 0)
    line_end = int(data.get("lines_end", 0) or 0)
    if line_start > 0 and line_end > 0:
        selected = lines[line_start-1:line_end]
        numbered = '\n'.join([f"{i+1:4d}|{l}" for i, l in enumerate(selected, start=line_start-1)])
        return jsonify({
            "success": True, "content": numbered,
            "path": str(target), "lines": total_lines, "range": f"{line_start}-{line_end}", "mode": "range", "cached": from_cache
        })
    
    # verify 参数：快速验证指定行是否匹配预期
    verify_line = int(data.get("verify_line", 0) or 0)
    verify_expected = data.get("verify_expected", "")
    if verify_line > 0 and verify_expected:
        if verify_line <= total_lines:
            actual = lines[verify_line - 1].rstrip()
            expected = verify_expected.rstrip()
            match = actual == expected
            return jsonify({
                "success": True,
                "verify": {"line": verify_line, "match": match, "actual": actual, "expected": expected},
                "path": str(target),
                "total_lines": total_lines,
                "hint": "代码已就绪，直接验证" if match else "代码与预期不符，请修改后重新验证"
            })
        else:
            return jsonify({"success": False, "error": f"行号 {verify_line} 超出文件范围 (1-{total_lines})"})

    # 全文带行号
    numbered = '\n'.join([f"{i+1:4d}|{l}" for i, l in enumerate(lines)])
    
    # status_hint: 在 content 顶部插入提示，打断逐段读取
    # status_hint: [临时关闭 - 经验注入隔离测试]
    filepath_str = str(target)
    # 规则1: 测试文件 → 提示直接验证
    if "test_" in filepath_str or filepath_str.endswith("_test.py"):
        if any("def test_" in l for l in lines):
            numbered = "[系统提示] 此文件包含测试用例定义，建议直接运行 python3 -c 验证而非逐行审查。\n\n" + numbered
    
    # 规则2: 源码文件包含目标方法 → 提示方法已就绪（配置化规则）
    METHOD_HINTS = [
        {
            "method": "def _calculate",
            "keywords": ["expression", "result", "return"],
            "hint": "此文件的 _calculate 方法已包含表达式返回格式，建议直接验证而非逐行审查。",
        },
    ]
    for rule in METHOD_HINTS:
        if any(rule["method"] in l for l in lines):
            if all(any(kw in l for l in lines) for kw in rule["keywords"]):
                numbered = f"[系统提示] {rule['hint']}\\n\\n" + numbered
                break

    # 连续读取计数器：≥5 次时提示停止探索
    global _consecutive_reads
    _consecutive_reads += 1
    hint = None
    if _consecutive_reads >= 5:
        hint = "已经连续读取了多个文件，建议基于已有信息直接操作，不要继续探索"

    return jsonify({
        "success": True, "content": numbered,
        "path": str(target), "lines": total_lines, "mode": "full", "cached": from_cache,
        **({"hint": hint} if hint else {})
    })
    

    return jsonify(result)

@app.route("/v9/sandbox/write", methods=["POST"])
def v9_sandbox_write():
    data = request.json or {}
    user_id = data.get("user_id", "default")
    session_id = data.get("session_id", "default")
    filepath = data.get("path", "")
    content = data.get("content", "")
    line = data.get("line", 0)  # 按行修改：指定行号
    
    if not filepath:
        return jsonify({"success": False, "error": "path 必填"})
    
    # 路径解析
    base = Path(f"data/projects/{user_id}/{session_id}")
    base.mkdir(parents=True, exist_ok=True)
    filepath_obj = Path(filepath)
    if filepath_obj.is_absolute() or str(filepath).startswith("data/projects/"):
        target = filepath_obj
    else:
        project_root = "clawsjoy_dev"
        try:
            state_file = base / "clawsjoy_dev" / ".agent_state.json"
            if state_file.exists():
                project_root = json.loads(state_file.read_text()).get("project_root", "clawsjoy_dev")
        except:
            pass
        if str(filepath) == project_root or str(filepath).startswith(f"{project_root}/"):
            target = base / filepath
        elif str(filepath).startswith("."):
            target = base / filepath
        else:
            target = base / project_root / filepath
    
    if not str(target.resolve()).startswith(str(base.resolve())):
        return jsonify({"success": False, "error": "路径越权"})
    
    try:
        # 按行修改模式：只替换指定行
        if line > 0 and content:
            original = target.read_text() if target.exists() else ""
            original_lines = original.split('\n')
            if line <= len(original_lines):
                original_lines[line - 1] = content
                target.write_text('\n'.join(original_lines), encoding='utf-8')
                _read_cache.pop(str(target.resolve()), None)
                return jsonify({"success": True, "path": str(target), "line": line, "mode": "line_replace"})
            else:
                return jsonify({"success": False, "error": f"行号 {line} 超出文件范围 (1-{len(original_lines)})"})
        
        # 完整写入模式
        if target.exists():
            original = target.read_text()
            _orig_lines = original.split(chr(10))
            _new_lines = content.split(chr(10))
            # 保护：content 行数远少于原文件，可能丢失内容
            if len(_new_lines) < len(_orig_lines) - 5:
                _example_line = _orig_lines[-1] if _orig_lines else "新行内容"
                return jsonify({
                    "success": False,
                    "error": f"完整写入模式下 content 只有 {len(_new_lines)} 行，原文件有 {len(_orig_lines)} 行。请改用 line 参数修改单行。",
                    "hint": f"write_file(path='{str(target)}', line=N, content='{_example_line.strip()[:80]}')"
                })
            backup = target.with_suffix(target.suffix + '.bak')
            backup.write_text(original)
        target.write_text(content, encoding='utf-8')
        # 记录 artifact
        import hashlib as _hl
        _old_hash = _content_hashes.get(str(target), "")
        _new_hash = _hl.md5(content.encode()).hexdigest()
        _content_hashes[str(target)] = _new_hash
        _session_key = f"{user_id}/{session_id}"
        _artifact = {
            "id": f"write_{_session_key}_{_new_hash[:8]}",
            "type": "file_modification",
            "file": str(target.relative_to(Path(f"data/projects/{user_id}/{session_id}"))),
            "content_hash": _new_hash,
            "old_hash": _old_hash,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        if _session_key not in _session_artifacts:
            _session_artifacts[_session_key] = []
        _session_artifacts[_session_key].append(_artifact)
        _read_cache.pop(str(target.resolve()), None)
        return jsonify({"success": True, "path": str(target), "mode": "full_write"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/v9/sandbox/list", methods=["POST"])
def v9_sandbox_list():
    data = request.json or {}
    user_id = data.get("user_id", "default")
    session_id = data.get("session_id", "default")
    dirpath = data.get("path", ".")
    recursive = data.get("recursive", False)
    base = Path(f"data/projects/{user_id}/{session_id}")
    base.mkdir(parents=True, exist_ok=True)
    path_obj = Path(dirpath)
    if path_obj.is_absolute() or str(dirpath).startswith("data/projects/"):
        target = path_obj
    else:
        # 从 agent_state 获取项目根目录
        project_root = "clawsjoy_dev"
        try:
            state_file = base / "clawsjoy_dev" / ".agent_state.json"
            if state_file.exists():
                agent_state = json.loads(state_file.read_text())
                project_root = agent_state.get("project_root", "clawsjoy_dev")
        except:
            pass
        if str(dirpath) == project_root or str(dirpath).startswith(f"{project_root}/"):
            target = base / dirpath
        elif str(dirpath).startswith("."):
            target = base / dirpath
        elif "/" not in str(dirpath) and str(dirpath) != project_root:
            target = base / dirpath  # session 根目录下的文件/目录
        else:
            target = base / project_root / dirpath
            if not target.exists():
                target = base / dirpath
    if not str(target.resolve()).startswith(str(base.resolve())):
        return jsonify({"success": False, "error": "路径越权"})
    if not target.exists():
        return jsonify({"success": True, "files": [], "dirs": [], "path": str(target), "hint": "目录不存在"})
    if recursive:
        files = [str(p.relative_to(base)) for p in target.rglob("*") if p.is_file()][:50]
        dirs = [p.name for p in target.rglob("*") if p.is_dir()]
    else:
        files = [p.name for p in target.iterdir() if p.is_file()][:20]
        dirs = [p.name for p in target.iterdir() if p.is_dir()]
    return jsonify({"success": True, "files": files, "dirs": dirs, "path": str(target)})

@app.route("/v9/sandbox/search", methods=["POST"])
def v9_sandbox_search():
    data = request.json or {}
    user_id = data.get("user_id", "default")
    session_id = data.get("session_id", "default")
    query = data.get("query", "")
    dirpath = data.get("path", ".")
    base = Path(f"data/projects/{user_id}/{session_id}")
    base.mkdir(parents=True, exist_ok=True)
    path_obj = Path(dirpath)
    if path_obj.is_absolute() or str(dirpath).startswith("data/projects/"):
        target = path_obj
    else:
        # 从 agent_state 获取项目根目录
        project_root = "clawsjoy_dev"
        try:
            state_file = base / "clawsjoy_dev" / ".agent_state.json"
            if state_file.exists():
                agent_state = json.loads(state_file.read_text())
                project_root = agent_state.get("project_root", "clawsjoy_dev")
        except:
            pass
        if str(dirpath) == project_root or str(dirpath).startswith(f"{project_root}/"):
            target = base / dirpath
        elif str(dirpath).startswith("."):
            target = base / dirpath
        elif "/" not in str(dirpath) and str(dirpath) != project_root:
            target = base / dirpath  # session 根目录下的文件/目录
        else:
            target = base / project_root / dirpath
            if not target.exists():
                target = base / dirpath
    if not str(target.resolve()).startswith(str(base.resolve())):
        return jsonify({"success": False, "error": "路径越权"})
    result = tool_executor.execute("search_tools", {"query": query, "path": str(target)})
    return jsonify(result)

@app.route("/v9/sandbox/query_index", methods=["POST"])
def v9_sandbox_query_index():
    """查询代码索引"""
    global _code_indexer
    import re as _re
    data = request.json or {}
    query = data.get("query", "")
    if not query:
        return jsonify({"success": False, "error": "query 必填"})
    if _code_indexer is None:
        from core.lib.code_indexer import CodeIndexer
        from pathlib import Path as _Path
        _uid = data.get("user_id", "default")
        _sid = data.get("session_id", "default")
        _sandbox_base = _Path(f"data/projects/{_uid}/{_sid}")
        _project_dir = _sandbox_base / "clawsjoy_dev" if (_sandbox_base / "clawsjoy_dev").exists() else _sandbox_base
        _code_indexer = CodeIndexer(project_root=str(_project_dir))
        if not _code_indexer._keyword_index:
            _code_indexer._load()
    if not _code_indexer._keyword_index:
        return jsonify({"success": False, "error": "代码索引尚未初始化"})
    # 快速路径：查询包含文件路径关键词时，直接用 AST 解析
    import re as _re
    import warnings
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    file_match = _re.search(r'([\w_]+\.py|[\w_]+_agent)', query)
    if file_match:
        target = file_match.group(1)
        matches = []
        for fpath in _code_indexer._keyword_index:
            if target in fpath:
                # 优先源码文件，排除测试和备份
                priority = 0
                is_test = 'test_' in fpath or '/tests/' in fpath or fpath.endswith('.bak')
                is_source = '/agents/' in fpath and not is_test
                if is_source:
                    priority = 2
                elif is_test:
                    priority = 0
                else:
                    priority = 1
                matches.append((priority, fpath))
        if matches:
            matches.sort(key=lambda x: x[0], reverse=True)
            best = matches[0][1]
            blocks = _code_indexer.parse_file(best)
            return jsonify({"success": True, "query": query, "file": best, "blocks": blocks, "mode": "ast_direct"})
    
    results = []
    query_lower = query.lower()
    for filepath, keywords in _code_indexer._keyword_index.items():
        match_score = 0
        for kw in keywords:
            if kw.lower() in query_lower or query_lower in kw.lower():
                match_score += 1
        if match_score > 0:
            blocks = _code_indexer.parse_file(filepath)
            results.append({
                "file": filepath,
                "keywords": keywords,
                "match_score": match_score,
                "blocks": blocks[:20]
            })
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return jsonify({"success": True, "query": query, "results": results[:10]})

@app.route("/v9/sandbox/exec", methods=["POST"])
def v9_sandbox_exec():
    data = request.json or {}
    user_id = data.get("user_id", "default")
    session_id = data.get("session_id", "default")
    command = data.get("command", "")

    cmd_name = command.split()[0] if command else ""
    
    # 读文件命令走缓存
    import re as _re
    cat_match = _re.search(r"""(?:cat|head|tail)\s+["']?([^"'\s|;]+)["']?""", command)
    py_match = _re.search(r"""open\(["']([^"']+)["']""", command)
    file_to_read = None
    if cat_match: file_to_read = cat_match.group(1)
    elif py_match: file_to_read = py_match.group(1)
    
    if file_to_read:
        base = Path(f"data/projects/{user_id}/{session_id}")
        # 补全路径
        if not file_to_read.startswith("clawsjoy_dev/") and not file_to_read.startswith("/"):
            file_to_read = "clawsjoy_dev/" + file_to_read
        target = base / file_to_read
        cache_key = str(target.resolve())
        if cache_key in _read_cache:
            return jsonify({"success": True, "stdout": _read_cache[cache_key], "stderr": "", "cached": True})

    # 如果是读文件命令，提示用 read_file
    read_cmds = ['cat', 'head', 'tail', 'grep']
    if cmd_name in read_cmds and not any(kw in command for kw in ['pytest', 'python', 'find', 'ls', 'wc']):
        return jsonify({
            "success": False,
            "error": f"不要用 {cmd_name} 或其他命令读文件。read_file 是唯一的读文件方式，它支持行号、行范围、关键词搜索。你需要的所有读文件功能都在 read_file 里。",
            "hint": "read_file(path='clawsjoy_dev/xxx.py', search='关键词')"
        })
    
    if cmd_name not in ALLOWED_COMMANDS:
        return jsonify({"success": False, "error": f"命令 '{cmd_name}' 不在白名单"})

    base = Path(f"data/projects/{user_id}/{session_id}")
    base.mkdir(parents=True, exist_ok=True)

    # 检测文件写入操作，清除对应缓存
    import re as _re2
    write_match = _re2.search(r"""(?:write|open\(.*['"]w['"]\))["']?([^"'\s|;]+)["']?""", command)
    if write_match:
        written_file = write_match.group(1)
        if not written_file.startswith("clawsjoy_dev/") and not written_file.startswith("/"):
            written_file = "clawsjoy_dev/" + written_file
        target = base / written_file
        _read_cache.pop(str(target.resolve()), None)

    try:
        import subprocess
        result = subprocess.run(command, shell=True, cwd=str(base),
                                capture_output=True, text=True, timeout=30)
        return jsonify({
            "success": True,
            "stdout": result.stdout[:2000],
            "stderr": result.stderr[:1000],
            "returncode": result.returncode
        })
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "命令超时 (30s)"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/v9/sandbox/edit", methods=["POST"])
def v9_sandbox_edit():
    data = request.json or {}
    user_id = data.get("user_id", "default")
    session_id = data.get("session_id", "default")
    filepath = data.get("path", "")
    prompt = data.get("prompt", "")  # 要修改的内容前文
    suffix = data.get("suffix", "")  # 要修改的内容后文
    
    if not filepath:
        return jsonify({"success": False, "error": "path 必填"})
    # 写文件前重置连续读取计数器
    global _consecutive_reads
    _consecutive_reads = 0

    
    base = Path(f"data/projects/{user_id}/{session_id}")
    base.mkdir(parents=True, exist_ok=True)
    path_obj = Path(filepath)
    if path_obj.is_absolute() or str(filepath).startswith("data/projects/"):
        target = path_obj
    else:
        project_root = "clawsjoy_dev"
        try:
            state_file = base / "clawsjoy_dev" / ".agent_state.json"
            if state_file.exists():
                project_root = json.loads(state_file.read_text()).get("project_root", "clawsjoy_dev")
        except:
            pass
        target = base / project_root / filepath if not str(filepath).startswith(f"{project_root}/") else base / filepath
    if not str(target.resolve()).startswith(str(base.resolve())):
        return jsonify({"success": False, "error": "路径越权"})
    
    if not target.exists():
        return jsonify({"success": False, "error": "文件不存在"})
    
    import threading as _th
    print(f"[V9] thread={_th.current_thread().name}, key_in_environ={'DEEPSEEK_API_KEY' in os.environ}, key_len={len(os.environ.get('DEEPSEEK_API_KEY',''))}")
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        return jsonify({"success": False, "error": "未配置 API Key"})
    
    try:
        import requests as _r
        resp = _r.post(
            "https://api.deepseek.com/beta/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
                "prompt": prompt,
                "suffix": suffix,
                "max_tokens": 2048,
            },
            timeout=60,
        )
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["text"]
            # 将 FIM 结果插入到文件中
            original = target.read_text()
            # 备份原文件
            backup = target.with_suffix(target.suffix + '.bak')
            backup.write_text(original)
            
            # FIM 精准替换：找到 prompt 和 suffix 在原文件中的位置，只替换中间部分
            original = target.read_text()
            
            # 在原文件中定位 prompt 和 suffix
            # 模糊匹配：忽略每行前导空白
            def _fuzzy_find(text, pattern):
                text_lines = [l.strip() for l in text.split('\n')]
                pattern_lines = [l.strip() for l in pattern.strip().split('\n') if l.strip()]
                if not pattern_lines:
                    return -1
                for i in range(len(text_lines) - len(pattern_lines) + 1):
                    if all(text_lines[i+j] == pattern_lines[j] for j in range(len(pattern_lines))):
                        return i
                return -1
            
            prompt_line = _fuzzy_find(original, prompt)
            suffix_line = _fuzzy_find(original, suffix)
            
            if prompt_line >= 0 and suffix_line >= 0:
                start = sum(len(l)+1 for l in original.split('\n')[:prompt_line])
                end = sum(len(l)+1 for l in original.split('\n')[:suffix_line+1])
                final = original[:start] + prompt + "\n" + content + "\n" + suffix + original[end:]
                target.write_text(final)
                return jsonify({"success": True, "content": content, "path": str(target)})
            else:
                return jsonify({
                    "success": False,
                    "error": "FIM match failed. Use write_file with full content.",
                    "hint": "write_file(path, full_content)"
                })
        return jsonify({"success": False, "error": f"API错误: {resp.status_code}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

#前端分别显示 — DeepSeek 余额 + GLM 余额 + 总花费(示例🔵 ¥98.50  🟣 ¥45.00  💰 ¥12.35)
@app.route("/v9/user/balance", methods=["GET"])
def v9_user_balance():
    import threading as _th
    print(f"[V9] thread={_th.current_thread().name}, key_in_environ={'DEEPSEEK_API_KEY' in os.environ}, key_len={len(os.environ.get('DEEPSEEK_API_KEY',''))}")
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        return jsonify({"success": False, "error": "未配置 API Key"})
    try:
        import requests as _r
        resp = _r.get(
            "https://api.deepseek.com/user/balance",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            balance_info = data.get("balance_infos", [{}])[0]
            return jsonify({
                "success": True,
                "available": data.get("is_available", False),
                "currency": balance_info.get("currency", "CNY"),
                "total": balance_info.get("total_balance", "0"),
                "topped_up": balance_info.get("topped_up_balance", "0"),
                "granted": balance_info.get("granted_balance", "0")
            })
        return jsonify({"success": False, "error": f"API错误: {resp.status_code}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/v9/glm/balance", methods=["GET"])
def v9_glm_balance():
    api_key = os.getenv("GLM_API_KEY", "")
    if not api_key:
        return jsonify({"success": False, "error": "未配置 GLM API Key"})
    try:
        import requests as _r
        resp = _r.get(
            "https://open.bigmodel.cn/api/paas/v4/user/balance",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            balance_info = data.get("balance_infos", [{}])[0] if data.get("balance_infos") else {}
            return jsonify({
                "success": True,
                "total": balance_info.get("total_balance", data.get("balance", "0")),
                "currency": balance_info.get("currency", "CNY"),
            })
        return jsonify({"success": False, "error": f"API错误: {resp.status_code}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/v9/balance", methods=["GET"])
def v9_balance():
    result = {"deepseek": {}, "glm": {}, "total_cost": 0}
    
    # DeepSeek 余额
    try:
        ds_key = os.getenv("DEEPSEEK_API_KEY", "")
        if ds_key:
            import requests as _r
            resp = _r.get("https://api.deepseek.com/user/balance",
                          headers={"Authorization": f"Bearer {ds_key}"}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                info = data.get("balance_infos", [{}])[0]
                result["deepseek"] = {"total": info.get("total_balance", "0"), "currency": "CNY"}
    except:
        pass
    
    # GLM 余额
    try:
        glm_key = os.getenv("GLM_API_KEY", "")
        if glm_key:
            resp = _r.get("https://open.bigmodel.cn/api/paas/v4/user/balance",
                         headers={"Authorization": f"Bearer {glm_key}"}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                result["glm"] = {"total": data.get("balance", "0"), "currency": "CNY"}
    except:
        pass
    
    # 总花费
    try:
        from core.lib.v8.ledger import ledger
        billing = ledger.get_billing("default")
        result["total_cost"] = round(billing.get("total", 0), 4)
    except:
        pass
    
    return jsonify({"success": True, **result})


def _estimate_tokens(messages):
    total = 0
    for m in messages:
        content = m.get("content", "") or ""
        total += len(content) * 0.5
        for tc in m.get("tool_calls", []):
            total += len(str(tc)) * 0.5
    return int(total)

def _compress_messages(messages, user_id):
    if len(messages) <= 8:
        return messages
    from core.lib.context_manager import get_context
    ctx = get_context(user_id)
    system_msg = messages[0] if messages[0]["role"] == "system" else None
    recent = messages[-6:]
    old_messages = messages[1:-6] if system_msg else messages[:-6]
    summary = ctx.inject() or ""
    compressed = []
    if system_msg:
        compressed.append(system_msg)
    if summary:
        compressed.append({"role": "system", "content": f"【历史摘要】{summary}"})
    compressed.extend(recent)
    return compressed


@app.route("/v9/agent/chat", methods=["POST"])
def v9_agent_chat():
    """代理 DeepSeek API 调用，前端不暴露 Key"""
    data = request.json or {}
    messages = data.get("messages", [])
    model = data.get("model", os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"))
    user_id = data.get("user_id", "default")  # 加这行
    session_id = data.get("session_id", "default")

    import threading as _th
    print(f"[V9] thread={_th.current_thread().name}, key_in_environ={'DEEPSEEK_API_KEY' in os.environ}, key_len={len(os.environ.get('DEEPSEEK_API_KEY',''))}")
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        return jsonify({
            "success": False, 
            "error": f"Key丢失! 启动时={'已加载' if _DEEPSEEK_KEY_LOADED.startswith('sk-') else '未加载'}，请求时为空",
            "loaded_at_startup": _DEEPSEEK_KEY_LOADED[:15] + "..." if _DEEPSEEK_KEY_LOADED.startswith('sk-') else _DEEPSEEK_KEY_LOADED
        })
    
    # 异步模式：启动后台任务
    async_mode = data.get("async", False)
    task_id = data.get("task_id", "")
    
    if async_mode and task_id and messages and messages[-1]["role"] == "user":
        _threading.Thread(
            target=_execute_agent_task,
            args=(user_id, session_id, messages, model, task_id),
            daemon=True
        ).start()
        return jsonify({
            "success": True, "status": "started", "task_id": task_id,
            "message": "任务已启动，可通过 /v9/task/<task_id> 查询状态"
        })

    # 复杂度预判：≥2个文件或≥3个修改意图时注入规划指令
    if messages and messages[-1]["role"] == "user":
        import re as _re
        user_msg = messages[-1]["content"]
        # 匹配 agent 名称模式（calculator_agent、analysis_agent 等）
        agent_count = len(_re.findall(r'\w+_agent', user_msg))
        # 匹配文件路径模式（agents/xxx/xxx.py 或 tools/xxx.py）
        file_count = len(_re.findall(r'(?:agents|tools)/[\w/]+\.py', user_msg))
        # 修改意图关键词
        modify_intents = sum(1 for kw in ["修改", "改", "重构", "提取", "统一", "合并", "拆分", "迁移"] if kw in user_msg)
        # 任一条件触发：≥2个agent 或 ≥2个文件路径 或 ≥3个修改意图
        if agent_count >= 2 or file_count >= 2 or modify_intents >= 3:
            messages[-1]["content"] = user_msg + "\n\n[系统指令] 此任务涉及多个文件或步骤，请先列出修改计划，询问用户确认后再执行。"

    # 加载 Prompt 模板
    prompt_template = Path("config/prompts/agent_system.md").read_text()
    
    sandbox_root = Path(f"data/projects/{user_id}/{session_id}").resolve()
    state_file = sandbox_root / "clawsjoy_dev" / ".agent_state.json"
    last_summary = ""
    venv_path = ".venv"
    project_root = "clawsjoy_dev"
    
    if state_file.exists():
        state = json.loads(state_file.read_text())
        venv_path = state.get("venv_path", ".venv")
        project_root = state.get("project_root", "clawsjoy_dev")
        installed = state.get("installed_packages", [])
        issues = state.get("known_issues", [])
        last_summary = f"上次任务：{state.get('last_task','')}。"
        if installed:
            last_summary += f"已安装包：{', '.join(installed[:8])}。"
        if issues:
            last_summary += f"已知问题：{'；'.join([i.get("issue", str(i)) for i in issues[:3]])}。"
    
    filled_prompt = prompt_template.format(
        sandbox_root=sandbox_root,
        venv_path=venv_path,
        project_root=project_root,
        last_session_summary=last_summary or "无",
        allowed_commands=", ".join(ALLOWED_COMMANDS)
    )
    
    if messages and messages[0]["role"] == "system":
        messages[0]["content"] = filled_prompt
    else:
        messages.insert(0, {"role": "system", "content": filled_prompt})
    
    # 模板填充后，追加上下文注入
    try:
        from core.lib.memory_bank import get_bank
        bank = get_bank(user_id)
        user_memory = bank.recall("preferences", limit=3)
        if user_memory and "未找到" not in user_memory:
            messages[0]["content"] += f"\n用户记忆：{user_memory}"
    
        from core.lib.vector_bank import get_vector_bank
        vbank = get_vector_bank(user_id)
        relevant = vbank.recall(messages[-1]["content"] if messages else "", limit=3)
        if relevant:
            messages[0]["content"] += f"\n相关历史：{[r.get('content','')[:100] for r in relevant]}"
    
        from core.lib.context_manager import get_context
        ctx = get_context(user_id)
        context_summary = ctx.inject()
        if context_summary:
            messages[0]["content"] += f"\n会话上下文：{context_summary}"
    except Exception as e:
        print(f"[V9] 上下文注入失败: {e}")

    # 新任务开始，清空 read_file 缓存，建立信任
    _read_cache.clear()
    
    # 从 .agent_state.json 注入 task_progress
    try:
        state_file = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev/.agent_state.json")
        if state_file.exists():
            agent_state = json.loads(state_file.read_text())
            tp = agent_state.get("task_progress")
            if tp:
                summary = "\n【系统】以下信息来自之前的任务记录：\n"
                for step in tp.get("completed_steps", []):
                    summary += f"- {step.get('action')}: {step.get('file', '')}\n"
                if tp.get("pending_steps"):
                    summary += f"待完成: {', '.join(tp['pending_steps'])}\n"
                issues = agent_state.get("known_issues", [])
                if issues:
                    summary += "已知问题:\n"
                    for i in issues[:3]:
                        summary += f"- {i.get('issue', str(i))}\n"
                tips = agent_state.get("optimization_tips", "")
                if tips:
                    summary += f"\n💡 优化建议: {tips}\n"
                messages[0]["content"] += summary
    except:
        pass

    # 注入历史任务步骤
    try:
        state_file = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev/.agent_state.json")
        if state_file.exists():
            agent_state = json.loads(state_file.read_text())
            tp = agent_state.get("task_progress")
            if tp and tp.get("completed_steps"):
                hint = "\n[系统] 以下步骤已在之前任务中完成，无需重复执行：\n"
                for s in tp["completed_steps"]:
                    if s.get("action") == "verified" and s.get("status") == "already_correct":
                        hint += "- 已验证代码处于目标状态，不需要修改\n"
                    else:
                        hint += f"- {s.get('file', '')} {s.get('action', '')}\n"
                hint += "\n请直接执行验证步骤，不要重新读取或修改代码。\n"
                hint += "验证方式：python3 -c 运行断言，不要用 pytest。"
                print(f"[V9] 历史任务注入: {len(tp.get('completed_steps',[]))} 步骤")
                if len(messages) > 0 and messages[-1]["role"] == "user":
                    messages[-1]["content"] = hint + "\n\n" + messages[-1]["content"]
                else:
                    messages[0]["content"] += hint
    except:
        pass

    # artifact 摘要注入
    _session_key = f"{user_id}/{session_id}"
    if _session_key in _session_artifacts:
        arts = _session_artifacts[_session_key]
        snapshots = [a for a in arts if a["type"] == "file_snapshot"]
        modifications = [a for a in arts if a["type"] == "file_modification"]
        if snapshots or modifications:
            summary = "\n【本次会话已执行的操作】\n"
            if snapshots:
                files = list(set(a["file"] for a in snapshots))
                summary += f"已读文件: {', '.join(files)}\n"
            if modifications:
                files = list(set(a["file"] for a in modifications))
                summary += f"已修改文件: {', '.join(files)}\n"
            summary += "不要重复读取或修改已完成的操作。"
            messages[0]["content"] += summary

    # ===== 代码预加载（用户级懒加载索引 + 关键词匹配 + embedding 精排） =====
    if messages and messages[-1]["role"] == "user":
        print("[V9] Preload triggered")
        try:
            from pathlib import Path as _Path
            
            sandbox_base = _Path(f"data/projects/{user_id}/{session_id}")
            project_dir = sandbox_base / "clawsjoy_dev" if (sandbox_base / "clawsjoy_dev").exists() else sandbox_base
            
            from core.lib.code_indexer import CodeIndexer
            indexer = CodeIndexer(project_root=str(project_dir))
            _code_indexer = indexer  # 模块级变量，供 _execute_sandbox_tool 使用
            
            index_file = project_dir / "data" / "code_index" / "keyword_index.json"
            print(f"[V9] index_file path: {index_file} exists: {index_file.exists()}")
            
            # 首次使用：后台初始化索引
            if not index_file.exists():
                print(f"[V9] First use, initializing code index...")
                import threading
                threading.Thread(target=indexer.auto_init, daemon=True).start()
                return jsonify({
                    "success": True,
                    "status": "initializing",
                    "message": "项目初始化中，请稍候...预计 10-30 秒",
                    "data": {"choices": [{"message": {"content": "🔧 正在分析项目代码结构，请稍候..."}}]}
                })
            
            if not indexer._keyword_index:
                indexer._load()

            
            # 检测是否需要中文关键词（首次会调 DeepSeek）

            kw_status = indexer._ensure_chinese_keywords()
            if kw_status.get("status") == "initializing":
                return jsonify({
                    "success": True,
                    "status": "initializing",
                    "message": "正在生成代码中文索引，请稍候...预计 3-5 秒",
                    "data": {"choices": [{"message": {"content": "🔧 正在生成代码中文索引，请稍候..."}}]}
                })
            
            task = messages[-1]["content"]
            matched_files = indexer.search_files(task, limit=5)
            
            if matched_files:
                top_blocks = indexer.search_blocks(task, files=matched_files, limit=5)
                files_to_load = list(set(b.get("file", "") for b in top_blocks if b.get("file")))
                if not files_to_load:
                    files_to_load = matched_files[:3]
                
                preload = "\n\n【项目代码 — 已自动加载，无需 read_file】\n"
                for f in files_to_load:
                    try:
                        file_path = project_dir / f
                        if file_path.exists():
                            file_content = file_path.read_text(encoding="utf-8")[:2000]
                            preload += f"\n--- {f} ---\n{file_content}\n"
                    except:
                        pass
                
                if "---" in preload:
                    if messages[0]["role"] == "system":
                        messages[0]["content"] += preload

        except Exception as e:
            print(f"[V9] Code preload failed (non-fatal): {e}")
    # ===== 预加载结束 =====
    
    # Token 超限保护（在调 API 之前）
    if _estimate_tokens(messages) > MAX_CONTEXT_TOKENS * 0.8:
        messages = _compress_messages(messages, user_id)
        print(f"[V9] 上下文已压缩，剩余 {len(messages)} 条消息")

    # 构建 tools 定义
    tools = _get_agent_tools()

    # 构建 tools 之后
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text())
            if state.get("skip_exploration"):
                tools = [t for t in tools if t["function"]["name"] not in ("list_dir", "search_files")]
        except:
            pass

    # 兜底拦截前端指令
    if messages and messages[-1]["role"] == "user":
        last_msg = messages[-1]["content"].strip().upper()
        if last_msg in ("/CLEAN", "/CLEAR"):
            return jsonify({"success": True, "data": {"choices": [{"message": {"content": "✅ 已清空"}}]}})
        if last_msg == "/RESTORE":
            base = Path(f"data/projects/{user_id}/{session_id}")
            restored = []
            for bak in base.rglob("*.bak"):
                orig = bak.with_suffix("")
                orig.write_text(bak.read_text())
                bak.unlink()
                restored.append(str(orig.name))
            return jsonify({"success": True, "data": {"choices": [{"message": {"content": f"✅ 已恢复: {', '.join(restored) if restored else '无备份文件'}"}}]}})
    # 调 DeepSeek API
    try:
        from core.lib.v8.adapters.deepseek_adapter import DeepSeekAdapter
        adapter = DeepSeekAdapter(api_key=api_key, model=model)
        resp = adapter.execute_with_tools(messages=messages, tools=tools, user_id=user_id, temperature=0.7, max_tokens=2000)

        if resp.get("success"):
            data_resp = resp["data"]
            tokens = resp.get("tokens", 0)


            # 记账
            try:
                from core.lib.v8.ledger import ledger
                ledger.record_cost(
                    server_id="default",
                    agent_name=f"agent_{user_id}",
                    position="Agent工作区",
                    model=model,
                    tokens=tokens,
                    unit_price=0.001,
                    task_id=user_id,
                    summary=f"Agent工作区调用 - tokens={tokens}"
                )
            except Exception as e:
                print(f"[V9] 记账失败: {e}")
            
            # ===== 元认知审查（复用 Metacognition + GLM）=====
            try:

                glm_key = os.getenv("GLM_API_KEY", "")
                if glm_key and len(messages) > 1:
                    from core.lib.metacognition import Metacognition
                    meta = Metacognition(f"agent_{user_id}")
                    
                    last_user = ""
                    for m in reversed(messages):
                        if m["role"] == "user":
                            last_user = m.get("content", "")[:200]
                            break
                    
                    behavior_log = []
                    for m in messages[-15:]:
                        if m["role"] == "tool":
                            behavior_log.append(m.get("content", "")[:100])
                        elif m["role"] == "assistant" and m.get("content"):
                            behavior_log.append(f"Agent: {m['content'][:80]}")

                    reflection = meta.reflect(
                        user_input=last_user,
                        response=f"Agent完成 {len(messages)} 轮对话",
                        behavior_log=behavior_log,
                        use_glm=True
                    )
                    
                    if len(meta.reflections) >= 10:
                        evolution = meta.evolve()
                        if evolution.get("suggestions"):
                            state["optimization_tips"] = "; ".join(evolution["suggestions"])
                    
                    state["last_review"] = datetime.now().isoformat()
            except Exception as e:
                print(f"[V9] 元认知审查失败: {e}")
            # ===== 元认知审查结束 =====
            
            # ===== 学习能力：持久化会话状态 =====
            try:
                project_dir = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev")
                project_dir.mkdir(parents=True, exist_ok=True)

                state_file = project_dir / ".agent_state.json"
                state = {}
                if state_file.exists():
                    state = json.loads(state_file.read_text())

                last_user_msg = ""
                for m in reversed(messages):
                    if m["role"] == "user":
                        last_user_msg = m["content"][:200]
                        break

                state["last_task"] = last_user_msg
                state["last_time"] = datetime.now().isoformat()
                state["venv_path"] = ".venv"
                state["project_root"] = "clawsjoy_dev"

                # 自动扫描已安装的包
                venv_lib = project_dir / ".venv" / "lib"
                if venv_lib.exists():
                    installed = list(state.get("installed_packages", []))
                    for p in venv_lib.rglob("*.dist-info"):
                        pkg = p.name.split("-")[0]
                        if pkg not in installed:
                            installed.append(pkg)
                    state["installed_packages"] = installed[:50]

                # 自动扫描项目结构
                core_dirs = [d.name for d in project_dir.iterdir() if d.is_dir() and not d.name.startswith(".")][:20]
                state["project_structure"] = core_dirs
                
                # 项目认知固化：首次探索后记录关键配置
                if "project_config" not in state:
                    state["project_config"] = {
                        "root_dir": "clawsjoy_dev",
                        "test_dir": "tests",
                        "source_dir": "agents",
                        "pytest_params": {
                            "disabled_plugins": ["launch-testing-ros"],
                            "ignore_files": ["tests/test_e2e.py"],
                            "pythonpath": ""
                        }
                    }

                # 自动记录成功的测试命令
                known_commands = state.get("known_commands", {})
                if not isinstance(known_commands, dict):
                    known_commands = {}
                
                # 提取成功的具体命令
                for m in messages:
                    if m["role"] == "assistant" and m.get("tool_calls"):
                        for tc in m["tool_calls"]:
                            if tc["function"]["name"] == "execute_command":
                                cmd = json.loads(tc["function"]["arguments"]).get("command", "")
                                if "pytest" in cmd:
                                    # 只存命令本身，不存输出
                                    known_commands["pytest"] = cmd[:200]
                                    break
                
                state["known_commands"] = known_commands


                # 记录任务执行进度
                task_progress = state.get("task_progress", {})
                task_progress["last_user_message"] = last_user_msg
                task_progress["total_rounds"] = len(messages)
                task_progress["last_action"] = "completed"
                # 从 messages 提取 write_file 成功的步骤
                extracted_steps = []
                for m in messages:
                    if m["role"] == "assistant" and m.get("tool_calls"):
                        for tc in m["tool_calls"]:
                            if tc["function"]["name"] == "write_file":
                                args = json.loads(tc["function"]["arguments"])
                                step = {"action": "write_file", "file": args.get("path", "")}
                                if "line" in args:
                                    step["line"] = args["line"]
                                    step["content"] = args.get("content", "")[:100]
                                extracted_steps.append(step)
                if extracted_steps:
                    task_progress["completed_steps"] = extracted_steps
                
                # 检测 Agent 的最终结论：如果判定"代码已处于目标状态"
                for m in reversed(messages):
                    if m["role"] == "assistant" and m.get("content"):
                        c = m["content"]
                        if "代码已处于目标状态" in c or "未做修改" in c or "已处于目标状态" in c:
                            detail = c.split("\n")[0][:100] if "\n" in c else c[:100]
                            task_progress["completed_steps"] = [{
                                "action": "verified",
                                "status": "already_correct",
                                "detail": detail,
                                "timestamp": datetime.now().isoformat()
                            }]
                            break
                
                state["task_progress"] = task_progress

                # 同步 V8 task_engine 状态
                try:
                    from core.lib.v8.task_engine import task_engine
                    server_id = "default"
                    user_tasks = task_engine.list(server_id)
                    for t in user_tasks:
                        if t.get("created_by") == user_id and t.get("status") == "running":
                            task_engine.transition(server_id, t["id"], "done",
                                comment=f"任务完成: {task_progress.get('total_rounds', 0)} 轮对话")
                except Exception:
                    pass

                # 自动从失败命令中提取 known_issues
                current_issues = state.get("known_issues", [])
                if not isinstance(current_issues, list):
                    current_issues = []
                existing_texts = {i.get("issue", "") for i in current_issues}
                
                for m in messages:
                    if m["role"] == "tool" and m.get("content"):
                        content_str = str(m.get("content", ""))
                        import re as _re
                        
                        # 白名单命令失败
                        if "不在白名单" in content_str:
                            match = _re.search(r"'(\w+)' 不在白名单", content_str)
                            if match:
                                cmd = match.group(1)
                                tip = f"{cmd} 命令不可用，用 python 替代"
                                if tip not in existing_texts:
                                    current_issues.append({"issue": tip})
                                    existing_texts.add(tip)
                        
                        # ModuleNotFoundError
                        if "ModuleNotFoundError" in content_str:
                            match = _re.search(r"No module named '([^']+)'", content_str)
                            if match:
                                mod = match.group(1)
                                tip = f"缺少模块 {mod}，需 --ignore 跳过相关测试"
                                if tip not in existing_texts:
                                    current_issues.append({"issue": tip})
                                    existing_texts.add(tip)
                        
                        # FileNotFoundError — 路径错误
                        if "FileNotFoundError" in content_str:
                            match = _re.search(r"No such file or directory: '([^']+)'", content_str)
                            if match:
                                path = match.group(1)
                                tip = f"路径不存在: {path.split('/')[-1] if '/' in path else path}，检查是否漏了 clawsjoy_dev/ 前缀"
                                if tip not in existing_texts:
                                    current_issues.append({"issue": tip})
                                    existing_texts.add(tip)
                        
                        # pytest 插件冲突
                        if "launch_testing" in content_str and "error" in content_str.lower():
                            tip = "pytest 需加 -p no:launch-testing-ros 禁用 ROS 插件"
                            if tip not in existing_texts:
                                current_issues.append({"issue": tip})
                                existing_texts.add(tip)
                        
                        # 路径越权
                        if "路径越权" in content_str:
                            tip = "路径越权，检查文件路径是否在项目目录内"
                            if tip not in existing_texts:
                                current_issues.append({"issue": tip})
                                existing_texts.add(tip)
                
                state["known_issues"] = current_issues[-10:]

                # 从 artifacts 自动沉淀经验
                _session_key = f"{user_id}/{session_id}"
                if _session_key in _session_artifacts:
                    arts = _session_artifacts[_session_key]
                    # 检测重复读取
                    hash_counts = {}
                    for a in arts:
                        if a["type"] == "file_snapshot":
                            h = a["content_hash"]
                            hash_counts[h] = hash_counts.get(h, 0) + 1
                    for h, cnt in hash_counts.items():
                        if cnt > 2:
                            tip = f"同一文件被读取{cnt}次，可能无效循环"
                            if tip not in existing_texts:
                                current_issues.append({"issue": tip})
                                existing_texts.add(tip)
                    
                    # 清理本次 artifacts
                    _session_artifacts.pop(_session_key, None)  # 保留最近10条

                # 提炼 known_patterns
                current_patterns = state.get("known_patterns", [])
                if not isinstance(current_patterns, list):
                    current_patterns = []
                
                has_write = any("write_file" in str(m.get("tool_calls", "")) for m in messages if m["role"] == "assistant")
                has_test = any("pytest" in str(m.get("content", "")) and "passed" in str(m.get("content", "")).lower() for m in messages if m["role"] == "tool")
                
                if has_write and has_test:
                    p = {"pattern": "修改源码 -> 写入 -> 测试验证", "trigger": "代码修改任务", "success": True, "timestamp": datetime.now().isoformat()}
                    if p["pattern"] not in [x.get("pattern") for x in current_patterns]:
                        current_patterns.append(p)
                
                has_search = any("search=" in str(m.get("tool_calls", "")) for m in messages if m["role"] == "assistant")
                has_lines = any("lines_start" in str(m.get("tool_calls", "")) for m in messages if m["role"] == "assistant")
                
                if has_search and has_lines:
                    p = {"pattern": "search定位 -> lines范围读取", "trigger": "需要定位代码时", "success": True, "timestamp": datetime.now().isoformat()}
                    if p["pattern"] not in [x.get("pattern") for x in current_patterns]:
                        current_patterns.append(p)
                
                state["known_patterns"] = current_patterns[-5:]
                
                # 提炼 tool_preferences
                tool_prefs = state.get("tool_preferences", {})
                if not isinstance(tool_prefs, dict):
                    tool_prefs = {}
                tool_counts = {}
                for m in messages:
                    if m["role"] == "assistant" and m.get("tool_calls"):
                        for tc in m["tool_calls"]:
                            name = tc["function"]["name"]
                            tool_counts[name] = tool_counts.get(name, 0) + 1
                total = sum(tool_counts.values()) or 1
                for name, count in tool_counts.items():
                    tool_prefs[name] = round(count / total, 2)
                state["tool_preferences"] = tool_prefs

                state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2))

           
            except Exception as e:
                print(f"[V9] 状态持久化失败: {e}")
            # 上下文管理器
            try:
                from core.lib.context_manager import get_context
                ctx = get_context(user_id)
                ctx.add_turn(last_user_msg, f"tokens={tokens}", "agent_workspace", {})
            except:
                pass
            # ===== 学习能力结束 =====

            # 如果还有 tool_calls，后台继续执行
            if data_resp.get("choices", [{}])[0].get("message", {}).get("tool_calls"):
                # 返回给前端当前状态，后台继续
                pass
            
            return jsonify({"success": True, "data": data_resp, "tokens": tokens})
        return jsonify({"success": False, "error": resp.get("error", "API错误")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ====================================================================
#  V5 业务 API（gateway_helpers 复活）
# ====================================================================

@app.route("/api/v5/user/state", methods=["GET"])
def get_user_state_api():
    from core.lib.gateway_helpers import get_user_state
    project_id = request.args.get("project_id")
    user_id = request.args.get("user_id", "default")
    return jsonify({"success": True, "state": get_user_state(project_id, user_id)})

@app.route("/api/v5/user/state", methods=["POST"])
def set_user_state_api():
    from core.lib.gateway_helpers import set_user_state
    data = request.json or {}
    set_user_state(data.get("project_id"), data.get("user_id", "default"), data.get("key"), data.get("value"))
    return jsonify({"success": True})

@app.route("/api/v5/learning/stats", methods=["GET"])
def learning_stats_api():
    from core.lib.gateway_helpers import load_learning_stats
    return jsonify({"success": True, "stats": load_learning_stats()})

@app.route("/api/v5/file/read", methods=["POST"])
def file_read_api():
    from core.lib.gateway_helpers import extract_file_content
    data = request.json or {}
    content, info = extract_file_content(data.get("project_id"), data.get("file_path"), data.get("user_id", "default"))
    return jsonify({"success": True, "content": content, "info": info})

@app.route("/api/v5/user/info", methods=["POST"])
def user_info_api():
    from core.lib.gateway_helpers import extract_user_info, answer_from_state
    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "default")
    project_id = data.get("project_id")
    extract_user_info(message, user_id, project_id)
    answer = answer_from_state(message, user_id, project_id)
    return jsonify({"success": True, "answer": answer})


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


