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
from typing import Optional
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
# 预热：提前加载模型到 GPU，避免首次请求超时
try:
    import threading as _th
    def _warmup():
        try:
            _req.post('http://127.0.0.1:11434/api/generate',
                      json={'model':'qwen2.5:7b-instruct-q4_0','prompt':'hi','stream':False,'options':{'num_predict':1}},
                      timeout=60)
        except:
            pass
    _th.Thread(target=_warmup, daemon=True).start()
except:
    pass
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
from web.api.video_studio_api import video_studio_bp

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
app.register_blueprint(video_studio_bp)

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
    try:

        state = json.loads(state_file.read_text())

    except:

        state = {} if state_file.exists() else {}
    
    state["task_progress"] = {
        "status": "paused",
        "original_task": progress.get("original_task", ""),
        "completed_steps": progress.get("completed_steps", []),
        "pending_steps": progress.get("pending_steps", []),
        "total_rounds": progress.get("total_rounds", 0),
        "paused_at": datetime.now().isoformat()
    }
    state_file.write_text(_safe_serialize_state(state))
    return jsonify({"ok": True})


@app.route("/v9/task/status", methods=["GET"])
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

@app.route("/data/videos/<path:filename>")
def serve_video(filename):
    from flask import send_from_directory
    return send_from_directory("data/videos", filename)


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
        _save_data = {
            "status": status, "content": content, "tokens": tokens,
            "updated": datetime.now().isoformat()
        }
        _last_usr = ""
        for _m in messages:
            if _m["role"] == "user":
                _last_usr = _m["content"]
        if _last_usr:
            _save_data["last_task"] = _last_usr[:200]
        state_file.write_text(_safe_serialize_state(_save_data))
    
    import threading as _th
    print(f"[V9] thread={_th.current_thread().name}, key_in_environ={'DEEPSEEK_API_KEY' in os.environ}, key_len={len(os.environ.get('DEEPSEEK_API_KEY',''))}")
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        _save_state("failed", "未配置 API Key")
        return
    
    try:
        tools = [
            {"type": "function", "function": {"name": "read_file", "strict": True, "description": "读取文件内容，自动带行号。支持行范围和关键词搜索。cached:true表示文件已读过未变化。读取测试文件时可能返回status_hint:\"tests_found\"提示可直接验证。", "parameters": {"type": "object", "additionalProperties": False, "properties": {"path": {"type": "string", "description": "文件路径"}, "search": {"type": "string", "description": "搜索关键词，返回匹配行"}, "lines_start": {"type": "integer", "description": "起始行号"}, "lines_end": {"type": "integer", "description": "结束行号"}, "verify_line": {"type": "integer", "description": "验证指定行号"}, "verify_expected": {"type": "string", "description": "期望的内容，与指定行比对返回match"}}, "required": ["path"]}}},
            {"type": "function", "function": {"name": "write_file", "strict": True, "description": "写入文件。支持按行修改：write_file(path, line=98, content=\"新行内容\")。也支持完整写入：write_file(path, content=\"完整内容\")。注释统一用#，不要用\"\"\"或'''。", "parameters": {"type": "object", "additionalProperties": False, "properties": {"path": {"type": "string"}, "content": {"type": "string"}, "line": {"type": "integer", "description": "line 参数限制：文件必须≤200行，且只修改1-2行。不满足任一条件时禁止使用 line，必须用完整写入（write_file 不带 line 参数，或 python3 heredoc）。如果 content 包含换行符，替换从 line 开始的多行；否则只替换该行"}}, "required": ["path"]}}},
            {"type": "function", "function": {"name": "list_dir", "strict": True, "description": "列出目录", "parameters": {"type": "object", "additionalProperties": False, "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
            {"type": "function", "function": {"name": "search_files", "strict": True, "description": "搜索文件", "parameters": {"type": "object", "additionalProperties": False, "properties": {"query": {"type": "string"}, "path": {"type": "string"}}, "required": ["query", "path"]}}},
            {"type": "function", "function": {"name": "execute_command", "strict": True, "description": "执行命令", "parameters": {"type": "object", "additionalProperties": False, "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
            {"type": "function", "function": {"name": "query_index", "strict": True, "description": "查询代码索引，返回结构化结果。用法：query_index(query='analysis_agent 有哪些方法') 或 query_index(query='谁调用了 _resp')", "parameters": {"type": "object", "additionalProperties": False, "properties": {"query": {"type": "string", "description": "自然语言查询"}}, "required": ["query"]}}},
        ]
        adapter = DeepSeekAdapter(api_key=api_key, model=model)
        max_rounds = 100
        total_tokens = 0
        
        # 前置检测：文件是否已满足任务需求（Agent 循环之前）
        _last_user_msg = ""
        for _m in reversed(messages):
            if _m["role"] == "user":
                _last_user_msg = _m["content"]
                break
        if _last_user_msg:
            import re as _re_pre
            _write_kw = ['添加', '创建', '修改', '新增', '加入', '实现', '编写', '补充']
            _has_write = any(kw in _last_user_msg for kw in _write_kw)
            if _has_write:
                _target_match = _re_pre.search(r'[\w_]+/[\w_]+\.\w+', _last_user_msg)
                if _target_match:
                    _target_file = _target_match.group(0)
                    _base = Path(f"data/projects/{user_id}/{session_id}")
                    _disk_paths = [
                        _base / _target_file,
                        _base / "clawsjoy_dev" / _target_file,
                    ]
                    _found = None
                    for _dp in _disk_paths:
                        if _dp.exists():
                            _found = _dp
                            break
                    if not _found:
                        import glob as _glob
                        _fname = _target_file.split("/")[-1]
                        _candidates = _glob.glob(str(_base / "**" / _fname), recursive=True)
                        for _c in _candidates:
                            _cp = Path(_c)
                            if _cp.exists() and "resume-optimizer" in str(_cp):
                                _found = _cp
                                break
                        if not _found:
                            for _c in _candidates:
                                _cp = Path(_c)
                                if _cp.exists():
                                    _found = _cp
                                    break
                    if _found:
                        try:
                            import ast as _ast_pre
                            _content = _found.read_text()
                            if _found.suffix == '.py':
                                _ast_pre.parse(_content)
                            _kw_raw = _re_pre.sub(r'[^一-鿿a-zA-Z0-9]', ' ', _last_user_msg)
                            _kw = _re_pre.findall(r'[一-鿿]{2,}|[a-zA-Z_]{3,}', _kw_raw)
                            _noise = {'resume', 'optimizer', 'analysis_page', 'py', 'markdown', '文件', '点击后将', '分析结果导出为'}
                            _action_pre = {'添加', '创建', '修改', '删除', '新增', '加入', '实现', '编写', '补充', '完善', '点击', '中添加', '点击后', '分析结果导出', '点击后将分析结果导出为'}
                            _kw = [k for k in _kw if k.lower() not in _noise and k not in _action_pre and not (k.isascii() and k.isalpha())]
                            _matched_pre = sum(1 for k in _kw if k.lower() in _content.lower())
                            if _kw and _matched_pre >= max(2, len(_kw) * 0.5):
                                _save_state("done", f"前置检测：文件已包含任务要求的功能（{', '.join(_kw[:5])}）", total_tokens)
                                return
                        except (SyntaxError, UnicodeDecodeError):
                            pass

        for _round in range(max_rounds):
            _thinking = len(_file_matches_hard) >= 2 if '_file_matches_hard' in dir() else False
            resp = adapter.execute_with_tools(
                messages=messages, tools=tools, user_id=user_id,
                temperature=0.7, max_tokens=8000 if _thinking else 2000, thinking=_thinking
            )
            
            if not resp.get("success"):
                _save_state("failed", resp.get("error", "API错误"))
                return
            
            data_resp = resp["data"]
            msg = data_resp.get("choices", [{}])[0].get("message", {})
            total_tokens += resp.get("tokens", 0)
            
            if not msg.get("tool_calls"):
                # 方案确认检测：Agent 在等待用户确认方案，不结束任务
                _content = msg.get("content", "")
                _confirmation_keywords = ["是否确认", "请确认", "按此计划", "确认后执行"]
                _scheme_indicators = ["```", "修改计划", "文件列表", "###", "| 文件 |", "实施步骤"]
                _has_confirmation = any(kw in _content for kw in _confirmation_keywords)
                _has_scheme = any(ind in _content for ind in _scheme_indicators)
                if _has_confirmation and _has_scheme:
                    continue  # 不结束任务，保留上下文等待用户输入
                # P0.5: 交付物检查 — 用户要求修改文件但未写入，不判定完成
                _last_user_msg = ""
                for _m in reversed(messages):
                    if _m["role"] == "user":
                        _last_user_msg = _m["content"]
                        break
                _write_keywords = ['创建', '修改', '完善', '写入', '新增', '添加', '生成', '实现', '编写', '补充', '新建']
                _has_write_intent = any(kw in _last_user_msg for kw in _write_keywords)
                if _has_write_intent:
                    _verification_keywords = ['已包含', '已存在', '已有', '无需修改', '已经实现', '已完成', '验证通过', '功能已完整实现']
                    _has_verified = any(kw in _content for kw in _verification_keywords)
                    if _has_verified:
                        _save_state("done", msg.get("content", ""), total_tokens)
                        return
                    # 第三步：系统主动检测 — Agent 读取的内容是否已满足任务需求
                    _consecutive_reads_on_target = 0
                    _last_read_content = ""
                    _recent_calls = []
                    for _m in messages[-10:]:
                        if _m["role"] == "assistant":
                            for _tc in _m.get("tool_calls", []):
                                _tc_name = _tc.get("function", {}).get("name", "")
                                _recent_calls.append(_tc_name)
                                if _tc_name == "read_file":
                                    try:
                                        _tc_args = json.loads(_tc["function"]["arguments"])
                                        _tc_path = _tc_args.get("path", "")
                                        if _tc_path == _target_hint or _tc_path.endswith('/' + _target_hint):
                                            _consecutive_reads_on_target += 1
                                    except:
                                        pass
                    if _consecutive_reads_on_target >= 3:
                        _recent_5 = _recent_calls[-5:]
                        _write_in_recent = any(c in ("write_file", "write_large") for c in _recent_5)
                        if not _write_in_recent:
                            for _m in reversed(messages):
                                if _m["role"] == "tool" and isinstance(_m.get("content"), str):
                                    _tool_content = _m["content"]
                                    if _tool_content and len(_tool_content) > len(_last_read_content):
                                        _last_read_content = _tool_content
                            if _last_read_content:
                                import re as _re7
                                _task_keywords = _re7.findall(r'[一-鿿]{2,4}|[a-zA-Z_]{3,}', _last_user_msg)
                                _action_words = {'添加', '创建', '修改', '删除', '新增', '加入', '实现', '编写', '补充', '完善'}
                                _noise_words = {'resume', 'optimizer', 'ui', 'analysis_page', 'py', 'markdown', '文件'}
                                _task_keywords = [k for k in _task_keywords if k.lower() not in _noise_words and k not in _action_words]
                                _matched_count = sum(1 for k in _task_keywords[:5] if k.lower() in _last_read_content.lower())
                                _matched = _matched_count >= 2 and (len(_task_keywords[:5]) == 0 or _matched_count >= len(_task_keywords[:5]) * 0.6)
                                if _matched and _task_keywords:
                                    _save_state("done", f"系统自动检测：文件已包含任务要求的功能（关键词匹配: {', '.join(_task_keywords[:5])}）", total_tokens)
                                    return
                    # 磁盘读取兜底：Agent 读取内容匹配失败时，直接从磁盘读取完整文件
                    import ast as _ast3
                    _target_disk_path = base / _target_hint if not _target_hint.startswith(str(base)) else Path(_target_hint)
                    if not _target_disk_path.exists():
                        _target_disk_path = base / "clawsjoy_dev" / _target_hint
                    if _target_disk_path.exists():
                        try:
                            _disk_content = _target_disk_path.read_text()
                            _ast3.parse(_disk_content)
                            _disk_matched_count = sum(1 for k in _task_keywords[:5] if k.lower() in _disk_content.lower())
                            _disk_matched = _disk_matched_count >= 2 and (len(_task_keywords[:5]) == 0 or _disk_matched_count >= len(_task_keywords[:5]) * 0.6)
                            if _disk_matched and _task_keywords:
                                _save_state("done", f"系统自动检测（磁盘）：文件已包含任务要求的功能（关键词匹配: {', '.join(_task_keywords[:5])}）", total_tokens)
                                return
                        except (SyntaxError, UnicodeDecodeError):
                            pass
                    _has_written = False
                    for _m in messages:
                        if _m["role"] == "assistant":
                            for _tc in _m.get("tool_calls", []):
                                if _tc.get("function", {}).get("name") == "write_file":
                                    _has_written = True
                                    break
                    if not _has_written:
                        import re as _re6
                        _target_hint = "目标文件"
                        _path_match = _re6.search(r'[\w_]+/[\w_]+\.\w+', _last_user_msg)
                        if _path_match:
                            _target_hint = _path_match.group(0)
                        messages.append({"role": "system", "content": f"[\u7cfb\u7edf] \u68c0\u6d4b\u5230\u4efb\u52a1\u672a\u6267\u884c\uff1a\u7528\u6237\u8981\u6c42\u4fee\u6539 {_target_hint}\uff0c\u4f46\u672a\u68c0\u6d4b\u5230 write_file \u64cd\u4f5c\u3002\u552f\u4e00\u53ef\u7528\u64cd\u4f5c\uff1awrite_file(path='{_target_hint}', content='\u5b8c\u6574\u6587\u4ef6\u5185\u5bb9')\u3002\u7981\u6b62\u7ee7\u7eed\u8bfb\u53d6\u6587\u4ef6\u3002\u8bf7\u7acb\u5373\u5199\u5165\u3002"})
                        continue
                # 任务完成
                _last_usr_sync = ""
                for _m_sync in messages:
                    if _m_sync["role"] == "user":
                        _last_usr_sync = _m_sync["content"]
                _sync_save = {"status": "done", "content": msg.get("content", ""), "tokens": total_tokens, "updated": datetime.now().isoformat()}
                if _last_usr_sync:
                    _sync_save["last_task"] = _last_usr_sync[:200]
                state_file = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev/.agent_state.json")
                try:
                    _existing = json.loads(state_file.read_text()) if state_file.exists() else {}
                except:
                    _existing = {}
                _existing.update(_sync_save)
                state_file.write_text(json.dumps(_existing, ensure_ascii=False, indent=2))
                return
            
            # 执行工具调用
            messages.append({"role": "assistant", "content": msg.get("content", ""), "tool_calls": msg["tool_calls"]})
            
            # 推送中间过程到状态文件
            if msg.get("content"):
                _save_state("running", msg["content"], total_tokens)
            for tc in msg["tool_calls"]:
                try:
                    args = _json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    # 尝试修复非法 JSON：补闭合引号、转义换行符
                    fixed = tc["function"]["arguments"]
                    if fixed.count('"') % 2 != 0:
                        fixed += '"'
                    fixed = fixed.replace('\n', '\\n').replace('\r', '\\r')
                    try:
                        args = _json.loads(fixed)
                    except json.JSONDecodeError:
                        _save_state("failed", f"工具参数 JSON 解析失败: {tc['function']['name']}")
                        return
                try:
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
            # P1: 前置拦截 — 查世界模型骨架
            _rel_path = str(target) if target else path
            _skeleton = _get_skeleton_by_path(_rel_path, user_id, session_id)
            _is_repeat = _is_repeat_read_attempt(messages, path)
            if _skeleton and not _is_repeat:
                return {
                    "success": True,
                    "cached": False,
                    "content": _skeleton,
                    "status_hint": "world_model_skeleton",
                    "hint": (
                        "以上是世界模型中的文件骨架（与磁盘文件一致）。"
                        "如果骨架信息足够完成当前任务，请直接 write_file，不需要 read_file。"
                        "如需查看完整文件内容，请再次调用 read_file。"
                    )
                }
            # P0-1: 读取硬限制
            import re as _re_limit
            _last_usr_msg = ""
            for _lm in messages:
                if _lm["role"] == "user":
                    _last_usr_msg = _lm["content"]
            _write_kw_limit = ['创建', '修改', '添加', '新增', '写入', '实现', '编写', '补充']
            _is_write_task = any(kw in _last_usr_msg for kw in _write_kw_limit)
            _max_reads = 5 if _is_write_task else 10
            if _consecutive_reads >= _max_reads and not any(
                tc.get("function", {}).get("name") in ("write_file", "write_large")
                for m in messages if m["role"] == "assistant"
                for tc in m.get("tool_calls", [])
            ):
                return {
                    "success": False,
                    "error": f"读取上限已达 {_max_reads} 个文件，请立即写入或声明完成。",
                    "hint": "分析阶段已完成，现在进入交付阶段。请使用 write_file 写入文件交付结果。"
                }
            result = tool_executor.execute("file_tools", {"action": "read", "path": str(target)})
            _consecutive_reads += 1
            from_cache = isinstance(result, dict) and result.get("cached", False)
            _fp_path = str(target) if target else ""
            if _is_stale_read(_fp_path, None, None, from_cache):
                if isinstance(result, dict):
                    result["success"] = False
                    result["error"] = "read_file 暂时不可用（同一位置连续 5 次缓存命中，无新信息）"
                    result["hint"] = "你已经反复读取了相同的内容。分析阶段已完成，现在进入交付阶段。请使用 write_file 写入文件交付结果。"
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
            _consecutive_lists = 0
            _last_read_fingerprints.clear()
            target = _resolve_path(base, args.get("path", ""))
            line = args.get("line", 0)
            content_str = args.get("content", "")
            # 修复模型双重转义：\n → 换行，\" → 引号
            content_str = content_str.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
            # 长内容自动走临时文件通道，避开 JSON 转义问题
            if len(content_str) > 2000:
                import tempfile as _tmp, os as _os
                _tf = _tmp.NamedTemporaryFile(mode='w', suffix='.tmp', delete=False, encoding='utf-8')
                try:
                    _tf.write(content_str)
                    _tf.close()
                    with open(_tf.name, 'r', encoding='utf-8') as _rf:
                        content_str = _rf.read()
                finally:
                    _os.unlink(_tf.name)
            # 截断保护：如果目标文件被部分读取过，禁止完整覆盖
            _truncated_read = False
            for _rm in messages:
                if _rm["role"] == "tool" and isinstance(_rm.get("content"), str):
                    try:
                        _rd = json.loads(_rm["content"]) if _rm["content"].startswith("{") else {}
                    except:
                        _rd = {}
                    if _rd.get("path") == str(target) and _rd.get("truncated"):
                        _truncated_read = True
                        break
            if _truncated_read and line == 0:
                return {
                    "success": False,
                    "error": "目标文件在本 session 中被截断读取过，禁止完整覆盖。请先用 read_file 读取完整文件内容，或使用 line 参数精确修改。",
                    "hint": f"文件有 {len(content_str.split(chr(10)))} 行，你只读取了前部分。用 read_file(path='{args.get("path")}') 获取完整内容后再写入。"
                }

            if line > 0:
                # 按行修改：支持单行和多行替换
                original_lines = target.read_text(encoding="utf-8").split("\n") if target.exists() else []
                # 硬约束：>200 行文件禁止 line 参数
                if len(original_lines) > 100:
                    return jsonify({
                        "success": False,
                        "error": f"文件 {len(original_lines)} 行，超过 100 行限制。请用完整写入（write_file 不带 line 参数）或 python3 heredoc。"
                    })
                if line <= len(original_lines):
                    content_lines = content_str.split("\n")
                    if len(content_lines) > 1:
                        end_line = line - 1 + len(content_lines)
                        if end_line <= len(original_lines):
                            original_lines[line - 1:end_line] = content_lines
                        else:
                            original_lines[line - 1:] = content_lines
                    else:
                        original_lines[line - 1] = content_str
                    target.write_text("\n".join(original_lines), encoding="utf-8")
                    if str(target).endswith('.js'):
                        import subprocess as _sp
                        _result = _sp.run(['node', '-c', str(target)], capture_output=True, text=True, timeout=10)
                        if _result.returncode != 0:
                            target.write_text("\n".join(original_lines), encoding="utf-8")
                            _key = str(target)
                            _js_rollback_count[_key] = _js_rollback_count.get(_key, 0) + 1
                            _count = _js_rollback_count[_key]
                            _err = _result.stderr[:200]
                            if _count >= 2:
                                return {"success": False, "error": f"write_file 已连续 {_count} 次导致 JS 语法错误并被回滚: {_err}", "hint": "write_file line 已被系统禁用。必须改用 python3 heredoc 完整写入该文件，不要再使用 write_file。", "line_mode_disabled": True}
                            else:
                                return {"success": False, "error": f"写入导致 JS 语法错误，已自动回滚: {_err}", "hint": "请改用 python3 heredoc 完整写入该文件，避免使用 write_file line 逐行修改。"}
                    return {"success": True, "line": line}
                else:
                    return {"success": False, "error": f"行号 {line} 超出文件范围 (1-{len(original_lines)})"}
            else:
                # 完整写入：行数保护 + 备份
                if target.exists():
                    original = target.read_text(encoding="utf-8")
                    orig_lines = original.split("\n")
                    new_lines = content_str.split("\n")
                    if len(new_lines) < len(orig_lines) - 5 and any(l1.strip() == l2.strip() for l1 in new_lines for l2 in orig_lines if l1.strip()):
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
    # 路径自动补全：缺少 clawsjoy_dev/ 前缀时尝试补全
    if not str(path).startswith(f"{project_root}/"):
        _corrected = f"{project_root}/{path}"
        if (base / _corrected).exists():
            return base / _corrected
    return base / project_root / path
# ===== 异步引擎结束 =====
_background_tasks = {}  # {task_id: {"status": "running", "result": None, "thread": Thread}}
_code_indexer = None  # CodeIndexer 实例，异步引擎可访问
_consecutive_reads = 0  # 连续 read_file 计数器
_consecutive_lists = 0  # 连续 list_dir 计数器
_last_read_fingerprints = []  # 最近 N 次读取指纹 (file, lines_start, lines_end)，用于斜率检测
_js_rollback_count = {}  # JS 语法回滚计数器，连续 2 次触发强制禁用 write_file line


def _extract_intent(content: str) -> Optional[dict]:
    """从 Agent 输出中提取任务意图"""
    plan_keywords = ["阶段", "步骤", "先做", "开发路线", "推荐", "建议"]
    if not any(kw in content for kw in plan_keywords):
        return None
    
    import re
    files = list(set(re.findall(r'`?([\w-]+/[\w-]+\.py)`?', content)))
    
    return {
        "source": "agent_plan",
        "files": files,
        "summary": content[:500],
        "extracted_at": datetime.now().isoformat()
    }

def _get_skeletons_by_type(module_type, user_id="default", session_id="default"):
    """从 world_model 中提取指定类型模块的骨架"""
    _state_file = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev/.agent_state.json")
    if not _state_file.exists():
        return None
    try:
        _state = json.loads(_state_file.read_text())
        _modules = _state.get("world_model", {}).get("modules", {})
        _skeletons = []
        for _fp, _info in _modules.items():
            if f"/{module_type}/" in _fp and _info.get("skeleton"):
                _skeletons.append(f"// {_fp}\n{_info['skeleton']}")
        return "\n\n".join(_skeletons[:3]) if _skeletons else None
    except:
        return None



def _record_path_pattern(original, resolved, user_id="default", session_id="default"):
    """记录路径使用模式（成功或修正）"""
    _state_file = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev/.agent_state.json")
    try:
        _state = json.loads(_state_file.read_text()) if _state_file.exists() else {}
        _patterns = _state.get("known_patterns", [])
        if not isinstance(_patterns, list):
            _patterns = []
        _pattern_type = "correction" if original != resolved else "success"
        _patterns.append({
            "type": _pattern_type,
            "original": original,
            "resolved": resolved,
            "timestamp": datetime.now().isoformat()
        })
        _state["known_patterns"] = _patterns[-20:]
        _tmp = _state_file.with_suffix(".tmp")
        _tmp.write_text(json.dumps(_state, ensure_ascii=False, indent=2))
        _tmp.replace(_state_file)
    except:
        pass

def _generate_project_tree(user_id="default", session_id="default"):
    """从磁盘扫描 + world_model 合并生成项目文件树"""
    _base = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev")
    if not _base.exists():
        return ""
    try:
        _paths = set()
        # 1. 磁盘扫描（覆盖所有文件，包括 .env、.md 等非 Python 文件）
        for _f in _base.rglob("*"):
            if _f.is_file() and not any(p in _f.parts for p in ('__pycache__', '.git', 'code_index', 'vector_db', '.agent_state.json', '.pytest_cache', 'node_modules', '.venv', 'venv', '__pycache__')):
                _rel = str(_f.relative_to(_base))
                _paths.add(_rel)
        # 2. world_model 补充（可能有 write_file 过但磁盘尚未写入的）
        _state_file = _base / ".agent_state.json"
        if _state_file.exists():
            _state = json.loads(_state_file.read_text())
            _wm = _state.get("world_model", {})
            if isinstance(_wm, str):
                _wm = json.loads(_wm)
            for _k in _wm.get("modules", {}):
                _rel = _k.split("clawsjoy_dev/")[-1] if "clawsjoy_dev/" in _k else _k
                _paths.add(_rel)
        if not _paths:
            return ""
        _sorted_paths = sorted(_paths)
        _tree_lines = ["clawsjoy_dev/"]
        _prefixes = set()
        # 先收集所有目录和文件，确定每个层级的最后一个节点
        _all_nodes = {}
        for _p in _sorted_paths:
            _parts = ["clawsjoy_dev"] + _p.split("/")
            for _i in range(1, len(_parts)):
                _parent = "/".join(_parts[:_i])
                _node = "/".join(_parts[:_i+1])
                if _parent not in _all_nodes:
                    _all_nodes[_parent] = []
                if _node not in _all_nodes[_parent]:
                    _all_nodes[_parent].append(_node)
        # 从磁盘 + world_model 获取文件元信息
        _meta = {}
        # world_model 优先（有函数签名和行数）
        try:
            _wm = json.loads(_state_file.read_text()).get("world_model", {})
            if isinstance(_wm, str):
                _wm = json.loads(_wm)
            for _fp, _info in _wm.get("modules", {}).items():
                _short = _fp.split("clawsjoy_dev/")[-1] if "clawsjoy_dev/" in _fp else _fp
                _lines = _info.get("lines", 0)
                _funcs = _info.get("functions", [])
                _classes = _info.get("classes", [])
                _parts = []
                if _lines:
                    _parts.append(f"{_lines}行")
                if _classes:
                    _parts.append("class " + ", ".join(_classes[:2]))
                if _funcs:
                    _parts.append(", ".join(_funcs[:3]))
                _meta[_short] = " (" + "; ".join(_parts) + ")" if _parts else ""
        except:
            pass
        # 磁盘补充：对未在 world_model 中的文件，获取行数
        for _p in _paths:
            if _p not in _meta:
                try:
                    _disk_f = _base / _p
                    if _disk_f.exists() and _disk_f.suffix == '.py':
                        _fc = _disk_f.read_text()
                        _fc_lines = len(_fc.split('\n'))
                        import re as _re_meta
                        _fc_funcs = _re_meta.findall(r'^def\s+(\w+)', _fc, _re_meta.MULTILINE)
                        _fc_classes = _re_meta.findall(r'^class\s+(\w+)', _fc, _re_meta.MULTILINE)
                        _parts = [f"{_fc_lines}行"]
                        if _fc_classes:
                            _parts.append("class " + ", ".join(_fc_classes[:2]))
                        if _fc_funcs:
                            _parts.append(", ".join(_fc_funcs[:3]))
                        _meta[_p] = " (" + "; ".join(_parts) + ")"
                except:
                    pass

        # 按层级输出
        def _render(_key, _depth):
            if _key in _all_nodes:
                _children = _all_nodes[_key]
                for _j, _child in enumerate(_children):
                    _name = _child.split("/")[-1]
                    _full = _child
                    if _full.startswith("clawsjoy_dev/"):
                        _full = _full[len("clawsjoy_dev/"):]
                    _extra = _meta.get(_full, "")
                    _is_last = (_j == len(_children) - 1)
                    _indent = "  " * _depth + ("└─ " if _is_last else "├─ ")
                    _tree_lines.append(f"{_indent}{_name}{_extra}")
                    _render(_child, _depth + 1)
        # 大项目（>50 文件）：用摘要替代完整树
        _total_files = len(_paths)
        if _total_files > 50:
            _tree_lines = ["clawsjoy_dev/"]
            _top_dirs = set()
            _key_files = []
            for _p in sorted(_paths):
                _parts = _p.split("/")
                if len(_parts) >= 1:
                    _top_dirs.add(_parts[0])
                if _p in ('app.py', 'config.py', 'requirements.txt', 'README.md', 'agent_gateway_enhanced.py', 'conftest.py') or _p.endswith('/__init__.py'):
                    continue
                if _p.endswith('.py') and '/' not in _p:
                    _key_files.append(_p)
            _tree_lines.append(f" 顶层目录: {', '.join(sorted(_top_dirs)[:15])}")
            if _key_files:
                _tree_lines.append(f" 入口文件: {', '.join(_key_files[:10])}")
        else:
            _render("clawsjoy_dev", 0)
        # 追加统计摘要
        _py_count = sum(1 for _p in _paths if _p.endswith('.py'))
        _total_files = len(_paths)
        _agent_count = len([_p for _p in _paths if _p.startswith('agents/') and _p.endswith('.py') and _p.count('/') == 1])
        if _total_files > 10:
            _summary = f"\n项目规模: {_total_files} 文件, {_py_count} Python 文件"
            if _agent_count:
                _summary += f", {_agent_count} 个 Agent"
            _tree_lines.append(_summary)
        return "\n".join(_tree_lines) if _tree_lines else ""
    except:
        return ""

def _get_skeleton_by_path(filepath, user_id="default", session_id="default"):
    """从 world_model 中提取单个文件的骨架"""
    import ast as _ast
    _state_file = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev/.agent_state.json")
    if not _state_file.exists():
        return None
    try:
        _state = json.loads(_state_file.read_text())
        _wm = _state.get("world_model", {})
        if isinstance(_wm, str):
            try:
                _wm = json.loads(_wm)
            except (json.JSONDecodeError, ValueError):
                try:
                    _wm = _ast.literal_eval(_wm)
                except (ValueError, SyntaxError):
                    return None
        if not isinstance(_wm, dict):
            return None
        _info = _wm.get("modules", {}).get(filepath, {})
        return _info.get("skeleton") if _info.get("skeleton") else None
    except:
        return None


def _is_repeat_read_attempt(messages, filepath):
    """检测 Agent 是否已经尝试读取过此文件（第二次读取放行）"""
    _count = 0
    for _m in messages:
        if _m["role"] == "assistant":
            for _tc in _m.get("tool_calls", []):
                if _tc.get("function", {}).get("name") == "read_file":
                    try:
                        _args = json.loads(_tc["function"]["arguments"])
                        if _args.get("path") == filepath:
                            _count += 1
                    except:
                        pass
    return _count >= 1


def _is_repeat_read_attempt_v2(filepath, user_id="default", session_id="default"):
    _state_file = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev/.agent_state.json")
    if not _state_file.exists():
        return False
    try:
        _state = json.loads(_state_file.read_text())
        _artifacts = _state.get("artifacts", [])
        _count = 0
        for _a in _artifacts:
            if _a.get("type") == "read_file" and _a.get("path", "").endswith(filepath):
                _count += 1
        return _count >= 1
    except:
        return False


def _update_world_model(filepath, content, user_id="default", session_id="default"):
    """write_file 成功后更新模块依赖图"""
    import re as _re3
    global _last_read_fingerprints  # 借用全局变量声明位置
    _state_file = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev/.agent_state.json")
    _state = json.loads(_state_file.read_text()) if _state_file.exists() else {}
    if "world_model" not in _state or not isinstance(_state.get("world_model"), dict):
        _state["world_model"] = {"modules": {}, "last_updated": ""}
    
    _modules = _state["world_model"].get("modules", {})
    if not isinstance(_modules, dict):
        _modules = {}
        _state["world_model"]["modules"] = _modules
    _skel = None
    if filepath.endswith(".py"):
        _lines = content.split('\n')
        if "ui/" in filepath:
            _skel_lines = []
            for _i, _l in enumerate(_lines):
                _stripped = _l.strip()
                if _stripped.startswith('#') and ('\u2500' in _l or '===' in _l):
                    _skel_lines.append(_l)
                elif any(kw in _l for kw in ['st.', 'import streamlit', 'def render', 'def _']):
                    _skel_lines.append(_l)
                elif 'st.columns' in _l:
                    _skel_lines.append(_l)
                elif _i > 0 and any(kw in _lines[_i-1] for kw in ['st.', 'st.columns', 'import streamlit', 'def render', 'def _']):
                    _skel_lines.append(_l)
            _skel = '\n'.join(_skel_lines)[:4000]
        elif "services/" in filepath:
            _skel_lines = []
            for _i, _l in enumerate(_lines):
                _stripped = _l.strip()
                if _stripped.startswith('def ') or _stripped.startswith('class '):
                    _skel_lines.append(_l)
                elif any(kw in _l for kw in ['import ', 'from ', 'API', 'PRICING', 'MODEL', 'DEFAULT', 'BASE_URL', 'TIMEOUT', 'MAX_', 'MIN_']):
                    _skel_lines.append(_l)
                elif _stripped.startswith('@'):
                    _skel_lines.append(_l)
                elif _i > 0 and _lines[_i-1].strip().startswith('def '):
                    if _stripped.startswith('"""') or _stripped.startswith("'''"):
                        _skel_lines.append(_l)
                    elif _stripped.startswith('#') and any(kw in _stripped for kw in ('\u529f\u80fd', '\u4f5c\u7528', '\u8bf4\u660e', '\u53c2\u6570', '\u8fd4\u56de')):
                        _skel_lines.append(_l)
                elif _stripped.startswith('#') and ('\u2500' in _l or '===' in _l):
                    _skel_lines.append(_l)
            _skel = '\n'.join(_skel_lines)[:3000]
        elif "models/" in filepath:
            _skel_lines = [l for l in _lines if any(kw in l for kw in ['@dataclass', 'class ', 'def ', 'from dataclasses', 'from typing', 'field', 'Optional', ':', '='])]
            _skel = '\n'.join(_skel_lines)[:3000]
    _modules[filepath] = {
        "lines": len(content.split('\n')),
        "imports": _re3.findall(r'^(?:from|import)\s+(\S+)', content, _re3.MULTILINE),
        "classes": _re3.findall(r'^class\s+(\w+)', content, _re3.MULTILINE),
        "functions": _re3.findall(r'^def\s+(\w+)', content, _re3.MULTILINE),
        "status": "complete",
        "skeleton": _skel
    }
    # 路径校验：文件是否在项目目录树下
    _proj_root = _state.get("project_root", "clawsjoy_dev")
    if not filepath.startswith(_proj_root + "/"):
        # path_mismatch 的文件不加入 world_model，避免跨项目污染
        _state["world_model"]["last_updated"] = datetime.now().isoformat()
        _state_file.write_text(_safe_serialize_state(_state))
        return
    _state["world_model"]["last_updated"] = datetime.now().isoformat()
    _state_file.write_text(_safe_serialize_state(_state))

def _is_stale_read(filepath, lines_start, lines_end, cached):
    """判断是否为无效重复读取——同一位置连续缓存命中"""
    global _last_read_fingerprints
    if not cached:
        _last_read_fingerprints.clear()
        return False
    fingerprint = (filepath, lines_start, lines_end)
    _last_read_fingerprints.append(fingerprint)
    if len(_last_read_fingerprints) >= 5:
        unique = set(_last_read_fingerprints[-5:])
        if len(unique) == 1:
            return True
    if len(_last_read_fingerprints) > 10:
        _last_read_fingerprints = _last_read_fingerprints[-10:]
    return False


def _safe_serialize_state(state: dict) -> str:
    """安全序列化 state，逐字段隔离，定位崩溃字段"""
    import json as _json, re as _re
    
    for key, value in state.items():
        try:
            _json.dumps({key: value}, ensure_ascii=False)
        except Exception as e:
            print(f"[V9] 崩溃字段: {key}, 错误: {e}, 类型: {type(value).__name__}, 前80字符: {str(value)[:80]!r}")
    
    safe_state = {}
    for key, value in state.items():
        if isinstance(value, str):
            s = value
            s = s.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            s = s.replace('"', '\\"')
            s = _re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)
            max_len = 200 if key == 'last_task' else 2000 if '.content' in key else 10000 if key == 'world_model' else 500
            safe_state[key] = s[:max_len]
        elif isinstance(value, dict):
            _serialized = json.dumps(value, ensure_ascii=False, default=str)
            safe_state[key] = (_serialized[:10000] + "...<TRUNCATED>") if len(_serialized) > 10000 else _serialized
        elif isinstance(value, list):
            clean_list = []
            for v in value[:10]:
                if isinstance(v, dict):
                    clean_list.append({k: str(v2)[:200] if isinstance(v2, str) else v2 for k, v2 in v.items()})
                elif isinstance(v, str):
                    clean_list.append(v[:500])
                else:
                    clean_list.append(v)
            safe_state[key] = clean_list
        elif isinstance(value, (int, float, bool, type(None))):
            safe_state[key] = value
        else:
            _serialized = json.dumps(value, ensure_ascii=False, default=str)
            safe_state[key] = (_serialized[:10000] + "...<TRUNCATED>") if len(_serialized) > 10000 else _serialized
    
    try:
        return _json.dumps(safe_state, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[V9] 最终序列化失败: {e}，使用 repr 兜底")
        fallback = {k: repr(v) if not isinstance(v, (str, int, float, bool, type(None))) else v for k, v in safe_state.items()}
        return _json.dumps(fallback, ensure_ascii=False, indent=2)

def _get_agent_tools():
    """返回 Agent 工具定义列表。新增工具只需改此处。"""
    return [
        {"type": "function", "function": {"name": "read_file", "strict": True, "description": "读取文件内容，自动带行号。支持行范围和关键词搜索。cached:true表示文件已读过未变化。读取测试文件时可能返回status_hint:\"tests_found\"提示可直接验证。", "parameters": {"type": "object", "additionalProperties": False, "properties": {"path": {"type": "string", "description": "文件路径"}, "search": {"type": "string", "description": "搜索关键词，返回匹配行"}, "lines_start": {"type": "integer", "description": "起始行号"}, "lines_end": {"type": "integer", "description": "结束行号"}, "verify_line": {"type": "integer", "description": "验证指定行号"}, "verify_expected": {"type": "string", "description": "期望的内容，与指定行比对返回match"}}, "required": ["path"]}}},
        {"type": "function", "function": {"name": "write_file", "strict": True, "description": "写入文件。支持按行修改：write_file(path, line=98, content=\"新行内容\")。也支持完整写入：write_file(path, content=\"完整内容\")。注释统一用#，不要用\"\"\"或'''。", "parameters": {"type": "object", "additionalProperties": False, "properties": {"path": {"type": "string"}, "content": {"type": "string"}, "line": {"type": "integer", "description": "line 参数限制：文件必须≤200行，且只修改1-2行。不满足任一条件时禁止使用 line，必须用完整写入（write_file 不带 line 参数，或 python3 heredoc）。如果 content 包含换行符，替换从 line 开始的多行；否则只替换该行"}}, "required": ["path"]}}},
        {"type": "function", "function": {"name": "list_dir", "strict": True, "description": "列出目录", "parameters": {"type": "object", "additionalProperties": False, "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
        {"type": "function", "function": {"name": "search_files", "strict": True, "description": "搜索文件", "parameters": {"type": "object", "additionalProperties": False, "properties": {"query": {"type": "string"}, "path": {"type": "string"}}, "required": ["query", "path"]}}},
        {"type": "function", "function": {"name": "execute_command", "strict": True, "description": "执行命令", "parameters": {"type": "object", "additionalProperties": False, "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
        {"type": "function", "function": {"name": "query_index", "strict": True, "description": "查询代码索引，返回结构化结果。用法：query_index(query='analysis_agent 有哪些方法') 或 query_index(query='谁调用了 _resp')", "parameters": {"type": "object", "additionalProperties": False, "properties": {"query": {"type": "string", "description": "自然语言查询"}}, "required": ["query"]}}},
    ]

def _persist_state(state: dict, state_file: Path) -> bool:
    """持久化 state 到文件，内部做完整异常处理和诊断日志"""
    try:
        state_file.write_text(_safe_serialize_state(state))
        return True
    except Exception as e:
        print(f"[V9] 状态持久化失败: {e}, 异常类型: {type(e).__name__}")
        import json as _json, traceback
        traceback.print_exc()
        for k, v in state.items():
            if isinstance(v, str):
                try:
                    _json.dumps({k: v}, ensure_ascii=False)
                except Exception as _je:
                    print(f"[V9] 崩溃字段: {k}, 错误: {_je}, 前100字符: {v[:100]!r}")
                    break
        return False

@app.route("/v9/sandbox/read", methods=["POST"])
def v9_sandbox_read():
    global _consecutive_reads
    data = request.json or {}
    user_id = data.get("user_id", "default")
    session_id = data.get("session_id", "default")
    global _consecutive_reads, _consecutive_lists
    filepath = data.get("path", "")
    # 新任务检测：同步重置 list 配额
    if _consecutive_reads == 0:
        _consecutive_lists = 0
    if not filepath:
        return jsonify({"success": False, "error": "path 必填"})
    base = Path(f"data/projects/{user_id}/{session_id}")
    base.mkdir(parents=True, exist_ok=True)
    # 路径自动补全：command 中的路径缺少 clawsjoy_dev/ 前缀时，注入前缀
    _cmd = data.get("command", "")
    if "clawsjoy_dev/" not in _cmd and "/" in _cmd:
        _hint = f"cd clawsjoy_dev && {_cmd}"
        # 不修改原命令，在提示中标注
    filepath_obj = Path(filepath)
    if filepath_obj.is_absolute() or str(filepath).startswith("data/projects/"):
        target = filepath_obj
    else:
        target = base / filepath
    # 路径自动补全：ui/、services/、models/ 开头且不在项目子目录下时，自动补全
    _path_str = str(target)
    if not any(d in _path_str for d in ['youtube-autopilot/', 'exam-prep/']) and _path_str.startswith(('ui/', 'services/', 'models/')):
        # 从 world_model 获取项目根目录
        _state_file = base / "clawsjoy_dev" / ".agent_state.json"
        _proj_root = "youtube-autopilot"
        if _state_file.exists():
            try:
                _state = json.loads(_state_file.read_text())
                _wm = _state.get("world_model", {})
                _proj_root = _wm.get("project_root", "youtube-autopilot")
            except:
                pass
        target = base / _proj_root / filepath
    # 通用路径补全：如果路径不以 clawsjoy_dev/ 开头且不存在，尝试加前缀
    if not target.exists() and not str(filepath).startswith("clawsjoy_dev/"):
        _corrected = base / "clawsjoy_dev" / filepath
        if _corrected.exists():
            target = _corrected
    if not str(target.resolve()).startswith(str(base.resolve())):
        return jsonify({"success": False, "error": "路径越权"})

    _record_path_pattern(data.get('path', ''), str(target.relative_to(base)) if str(target).startswith(str(base)) else str(target), user_id, session_id)
    
    # artifact 采集
    _session_key = f"{user_id}/{session_id}"
    _start_time = __import__('time').time()
    
    # P1: 前置拦截 — 查世界模型骨架（v9_sandbox_read 路由）
    _rel_path = str(target) if target else filepath
    _skeleton = _get_skeleton_by_path(_rel_path, user_id, session_id)
    _is_repeat = _is_repeat_read_attempt_v2(filepath, user_id, session_id)
    if _skeleton and not _is_repeat:
        return jsonify({
            "success": True,
            "cached": False,
            "content": _skeleton,
            "status_hint": "world_model_skeleton",
            "hint": "以上是世界模型中的文件骨架（与磁盘文件一致）。如果骨架信息足够完成当前任务，请直接 write_file，不需要 read_file。如需查看完整文件内容，请再次调用 read_file。"
        })

    # P0-1: 读取硬限制（v9_sandbox_read 路由）
    _write_kw_v9 = ["创建", "修改", "添加", "新增", "写入", "实现", "编写", "补充"]
    _is_write_v9 = any(kw in str(data.get("_last_user_msg", "")) for kw in _write_kw_v9)
    _max_reads_v9 = 5 if _is_write_v9 else 10
    if _consecutive_reads >= _max_reads_v9:
        return jsonify({
            "success": False,
            "error": f"读取上限已达 {_max_reads_v9} 个文件，请立即写入或声明完成。",
            "hint": "分析阶段已完成，现在进入交付阶段。请使用 write_file 写入文件交付结果。"
        })

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
    # 斜率检测：同一位置连续 5 次缓存命中 → 无效循环
    _consecutive_reads += 1
    _line_start = line_start if 'line_start' in dir() else None
    _line_end = line_end if 'line_end' in dir() else None
    if _is_stale_read(str(target), _line_start, _line_end, from_cache):
        return jsonify({
            "success": False,
            "error": "read_file 暂时不可用（同一位置连续 5 次缓存命中，无新信息）",
            "hint": "你已经反复读取了相同的内容。分析阶段已完成，现在进入交付阶段。请使用 write_file 写入文件交付结果，不要继续读取。",
            "_consecutive_reads": _consecutive_reads
        })

    _truncated = len(numbered.split("\n")) < total_lines if total_lines > 0 else False
    return jsonify({
        "success": True, "content": numbered,
        "path": str(target), "lines": total_lines, "mode": "full", "cached": from_cache,
        "truncated": _truncated,

    })
    

    return jsonify(result)

@app.route("/v9/sandbox/write_large", methods=["POST"])
def v9_sandbox_write_large():
    """长内容写入——三层自动修复 + 降级信号"""
    import logging as _log
    data = request.json or {}
    user_id = data.get("user_id", "default")
    session_id = data.get("session_id", "default")
    filepath = data.get("path", "")
    raw = data.get("raw_arguments", "")
    content = ""
    auto_fixed = True
    fix_method = "json_parse"
    # ★ 主动 base64 通道：长内容网关直接写入，不返回给 Agent
    _pre_content = None
    try:
        _pre_args = json.loads(raw)
        _pre_content = _pre_args.get("content", "")
    except:
        pass
    if not _pre_content:
        import re as _re4
        _match = _re4.search(r'"content"\s*:\s*"', raw)
        if _match:
            _start = _match.end()
            _end = _start
            while _end < len(raw):
                if raw[_end] == '"' and (_end == 0 or raw[_end-1] != '\\'):
                    _after = raw[_end+1:_end+10].lstrip()
                    if _after.startswith(',') or _after.startswith('}'):
                        break
                _end += 1
            if _end > _start:
                _pre_content = raw[_start:_end]
                _pre_content = _pre_content.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
    if _pre_content and (_pre_content.count('\n') > 100 or len(_pre_content) > 3000):
        try:
            _base = Path(f"data/projects/{user_id}/{session_id}")
            _base.mkdir(parents=True, exist_ok=True)
            _target = _resolve_path(_base, filepath)
            _target.parent.mkdir(parents=True, exist_ok=True)
            _target.write_text(_pre_content, encoding='utf-8')
            _update_world_model(str(_target), _pre_content, user_id, session_id)
            return jsonify({
                "success": True,
                "auto_fixed": True,
                "fix_method": "direct_write",
                "path": str(_target),
                "size": len(_pre_content),
                "hint": "长内容已直接写入，请用 read_file 验证。"
            })
        except Exception as _e:
            _log.getLogger('werkzeug').exception(f'[DIRECT_WRITE_FAIL]')
            pass

    # 第一层：json.loads 直接解析
    try:
        args = json.loads(raw)
        content = args.get("content", "")
    except:
        # 第二层：字符串修复 + json.loads 重试
        try:
            fixed = raw
            if fixed.count('"') % 2 != 0:
                fixed += '"'
            fixed = fixed.replace('\n', '\\n').replace('\r', '\\r')
            args = json.loads(fixed)
            content = args.get("content", "")
            fix_method = "string_fix"
        except:
            # 第三层：正则提取 content + 反转义
            import re as _re
            match = _re.search(r'"content"\s*:\s*"', raw)
            if match:
                start = match.end()
                end_match = _re.search(r'"\s*}\s*$|"\s*,\s*"line"', raw[start:])
                if end_match:
                    content = raw[start:start + end_match.start()]
                    content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
                    fix_method = "regex_extract"
            # 第四层：正则盲区兜底 —— 逐字符扫描找 content 闭合引号
            if not content:
                start_marker = '"content": "'
                start_idx = raw.find(start_marker)
                if start_idx != -1:
                    start_idx += len(start_marker)
                    # 逐字符扫描：找第一个后面紧跟 , 或 } 的未转义引号
                    end_idx = start_idx
                    i = start_idx
                    while i < len(raw):
                        if raw[i] == '"' and (i == 0 or raw[i-1] != '\\'):
                            after = raw[i+1:i+10].lstrip()
                            if after.startswith(',') or after.startswith('}'):
                                end_idx = i
                                break
                        i += 1
                    if end_idx > start_idx:
                        content = raw[start_idx:end_idx]
                        content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
                        fix_method = "string_fallback"
                        content = raw[start_idx:end_idx]
                        content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
                        fix_method = "string_fallback"
    
    if not content:
        auto_fixed = False
    
    base = Path(f"data/projects/{user_id}/{session_id}")
    base.mkdir(parents=True, exist_ok=True)
    # 路径自动补全：command 中的路径缺少 clawsjoy_dev/ 前缀时，注入前缀
    _cmd = data.get("command", "")
    if "clawsjoy_dev/" not in _cmd and "/" in _cmd:
        _hint = f"cd clawsjoy_dev && {_cmd}"
        # 不修改原命令，在提示中标注
    target = _resolve_path(base, filepath)
    
    if content:
        target.write_text(content, encoding='utf-8')
    
    import base64 as _b64
    content_b64 = None
    hint_msg = None
    if not auto_fixed:
        content_b64 = _b64.b64encode(raw.encode()).decode()
        hint_msg = (
    "[系统指令] 唯一可用的写入方式是执行以下命令，立即复制执行：\n"
    f"python3 << 'PYEOF'\n"
    "import base64\n"
    f"content = base64.b64decode('{content_b64}').decode()\n"
    f"with open('{filepath}', 'w') as f:\n"
    "    f.write(content)\n"
    "PYEOF"
)

    return jsonify({
        "success": True,
        "auto_fixed": auto_fixed,
        "fix_method": fix_method if auto_fixed else None,
        "hint": hint_msg,
        "content_b64": content_b64,

    })


@app.route("/v9/sandbox/write_begin", methods=["POST"])
def v9_sandbox_write_begin():
    """返回临时文件路径"""
    import uuid as _uuid
    data = request.json or {}
    _temp_name = f"agent_write_{_uuid.uuid4().hex[:12]}.py"
    _temp_path = Path(f"/tmp/clawsjoy_temp/{_temp_name}")
    _temp_path.parent.mkdir(parents=True, exist_ok=True)
    return jsonify({"success": True, "temp_path": str(_temp_path)})


@app.route("/v9/sandbox/write_finalize", methods=["POST"])
def v9_sandbox_write_finalize():
    """将临时文件移动到目标路径"""
    data = request.json or {}
    user_id = data.get("user_id", "default")
    session_id = data.get("session_id", "default")
    target_path = data.get("path", "")
    temp_path = data.get("temp_path", "")
    if not target_path or not temp_path:
        return jsonify({"success": False, "error": "path 和 temp_path 必填"})
    _temp = Path(temp_path)
    if not _temp.exists():
        return jsonify({"success": False, "error": f"临时文件不存在: {temp_path}"})
    base = Path(f"data/projects/{user_id}/{session_id}")
    target = _resolve_path(base, target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    _temp.rename(target)
    _content = target.read_text(encoding='utf-8')
    _update_world_model(str(target), _content, user_id, session_id)
    return jsonify({"success": True, "path": str(target), "size": len(_content)})


@app.route("/v9/sandbox/write", methods=["POST"])
def v9_sandbox_write():
    data = request.json or {}
    user_id = data.get("user_id", "default")
    session_id = data.get("session_id", "default")
    filepath = data.get("path", "")
    content = data.get("content", "")
    line = data.get("line", 0)  # 按行修改：指定行号
    # 修复模型双重转义：\n → 换行，\" → 引号
    content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
    # 长内容自动走临时文件通道，避开 JSON 转义问题
    if len(content) > 2000:
        import tempfile as _tmp, os as _os
        _tf = _tmp.NamedTemporaryFile(mode="w", suffix=".tmp", delete=False, encoding="utf-8")
        try:
            _tf.write(content)
            _tf.close()
            with open(_tf.name, "r", encoding="utf-8") as _rf:
                content = _rf.read()
        finally:
            _os.unlink(_tf.name)

    
    global _consecutive_reads
    if not filepath:
        return jsonify({"success": False, "error": "path 必填"})
    
    # 路径解析
    base = Path(f"data/projects/{user_id}/{session_id}")
    base.mkdir(parents=True, exist_ok=True)
    # 路径自动补全：command 中的路径缺少 clawsjoy_dev/ 前缀时，注入前缀
    _cmd = data.get("command", "")
    if "clawsjoy_dev/" not in _cmd and "/" in _cmd:
        _hint = f"cd clawsjoy_dev && {_cmd}"
        # 不修改原命令，在提示中标注
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
    
    # 路径自动补全：ui/、services/、models/ 开头且不在项目子目录下时，自动补全
    _path_str = str(target)
    if not any(d in _path_str for d in ['youtube-autopilot/', 'exam-prep/']) and _path_str.startswith(('ui/', 'services/', 'models/')):
        # 从 world_model 获取项目根目录
        _state_file = base / "clawsjoy_dev" / ".agent_state.json"
        _proj_root = "youtube-autopilot"
        if _state_file.exists():
            try:
                _state = json.loads(_state_file.read_text())
                _wm = _state.get("world_model", {})
                _proj_root = _wm.get("project_root", "youtube-autopilot")
            except:
                pass
        target = base / _proj_root / filepath
    # 通用路径补全：如果路径不以 clawsjoy_dev/ 开头且不存在，尝试加前缀
    if not target.exists() and not str(filepath).startswith("clawsjoy_dev/"):
        _corrected = base / "clawsjoy_dev" / filepath
        if _corrected.exists():
            target = _corrected
    if not str(target.resolve()).startswith(str(base.resolve())):
        return jsonify({"success": False, "error": "路径越权"})

    _record_path_pattern(data.get('path', ''), str(target.relative_to(base)) if str(target).startswith(str(base)) else str(target), user_id, session_id)
    
    try:
        # 按行修改模式：支持单行和多行替换
        if line > 0 and content:
            original = target.read_text() if target.exists() else ""
            original_lines = original.split('\n')
            # 硬约束：>200 行文件禁止 line 参数
            if len(original_lines) > 100:
                return jsonify({
                    "success": False,
                    "error": f"文件 {len(original_lines)} 行，超过 100 行限制。请用完整写入（write_file 不带 line 参数）或 python3 heredoc。"
                })
            if line <= len(original_lines):
                content_lines = content.split('\n')
                if len(content_lines) > 1:
                    # 多行替换：替换从 line 开始的 len(content_lines) 行
                    end_line = line - 1 + len(content_lines)
                    if end_line <= len(original_lines):
                        original_lines[line - 1:end_line] = content_lines
                    else:
                        original_lines[line - 1:] = content_lines
                else:
                    # 单行替换
                    original_lines[line - 1] = content
                target.write_text('\n'.join(original_lines), encoding='utf-8')
                _read_cache.pop(str(target.resolve()), None)
                _consecutive_reads = 0
                _last_read_fingerprints.clear()
                _js_rollback_count.pop(str(target), None)
                # JS 文件写入后语法校验，失败则回滚
                if str(target).endswith('.js'):
                    import subprocess as _sp
                    _result = _sp.run(['node', '-c', str(target)], capture_output=True, text=True, timeout=10)
                    if _result.returncode != 0:
                        target.write_text('\n'.join(original_lines), encoding='utf-8')
                        _key = str(target)
                        _js_rollback_count[_key] = _js_rollback_count.get(_key, 0) + 1
                        _count = _js_rollback_count[_key]
                        _err = _result.stderr[:200]
                        if _count >= 2:
                            return jsonify({"success": False, "error": f"write_file 已连续 {_count} 次导致 JS 语法错误并被回滚: {_err}", "hint": "write_file line 已被系统禁用。必须改用 python3 heredoc 完整写入该文件，不要再使用 write_file。", "line_mode_disabled": True})
                        else:
                            return jsonify({"success": False, "error": f"写入导致 JS 语法错误，已自动回滚: {_err}", "hint": "请改用 python3 heredoc 完整写入该文件，避免使用 write_file line 逐行修改。"})
                return jsonify({"success": True, "path": str(target), "line": line, "mode": "line_replace"})
            else:
                return jsonify({"success": False, "error": f"行号 {line} 超出文件范围 (1-{len(original_lines)})"})
        
        # 完整写入模式
        if not content.strip():
            return jsonify({"success": False, "error": "content 为空，写入失败。请检查内容是否正确。"})
        if target.exists():
            original = target.read_text()
            _orig_lines = original.split(chr(10))
            _new_lines = content.split(chr(10))
            # 保护：content 行数远少于原文件，可能丢失内容
            if len(_new_lines) < len(_orig_lines) - 5 and any(l1.strip() == l2.strip() for l1 in _new_lines for l2 in _orig_lines if l1.strip()):
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
        _consecutive_reads = 0
        _update_world_model(str(target), content, user_id, session_id)
        return jsonify({"success": True, "path": str(target), "mode": "full_write"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/v9/sandbox/list", methods=["POST"])
def v9_sandbox_list():
    global _consecutive_reads
    data = request.json or {}
    # P0-1-ext: list_dir 配额限制（最多 3 次）
    global _consecutive_lists, _consecutive_reads
    # 新任务检测：如果 _consecutive_reads 为 0，说明是新任务，重置 list 配额
    if _consecutive_reads == 0:
        _consecutive_lists = 0
    _consecutive_lists += 1
    if _consecutive_lists > 3 and not data.get("skip_quota"):
        return jsonify({
            "success": False,
            "error": "list_dir 配额已达 3 次。请参考上下文中已注入的项目树获取目录结构。",
            "hint": "项目树与磁盘实时同步，包含所有文件路径。无需继续 list_dir。"
        })
    user_id = data.get("user_id", "default")
    session_id = data.get("session_id", "default")
    dirpath = data.get("path", ".")
    recursive = data.get("recursive", False)
    base = Path(f"data/projects/{user_id}/{session_id}")
    base.mkdir(parents=True, exist_ok=True)
    # 路径自动补全：command 中的路径缺少 clawsjoy_dev/ 前缀时，注入前缀
    _cmd = data.get("command", "")
    if "clawsjoy_dev/" not in _cmd and "/" in _cmd:
        _hint = f"cd clawsjoy_dev && {_cmd}"
        # 不修改原命令，在提示中标注
    path_obj = Path(dirpath)
    if path_obj.is_absolute() or str(dirpath).startswith("data/projects/"):
        target = path_obj
    else:
        # 从 agent_state 获取项目根目录
        project_root = "clawsjoy_dev"
        try:
            state_file = base / "clawsjoy_dev" / ".agent_state.json"
            if state_file.exists():
                try:

                    agent_state = json.loads(state_file.read_text())

                except:

                    agent_state = {}
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
    # 路径自动补全：ui/、services/、models/ 开头且不在项目子目录下时，自动补全
    _path_str = str(target)
    if not any(d in _path_str for d in ['youtube-autopilot/', 'exam-prep/']) and _path_str.startswith(('ui/', 'services/', 'models/')):
        # 从 world_model 获取项目根目录
        _state_file = base / "clawsjoy_dev" / ".agent_state.json"
        _proj_root = "youtube-autopilot"
        if _state_file.exists():
            try:
                _state = json.loads(_state_file.read_text())
                _wm = _state.get("world_model", {})
                _proj_root = _wm.get("project_root", "youtube-autopilot")
            except:
                pass
        target = base / _proj_root / filepath
    # 通用路径补全：如果路径不以 clawsjoy_dev/ 开头且不存在，尝试加前缀
    if not target.exists() and not str(dirpath).startswith("clawsjoy_dev/"):
        _corrected = base / "clawsjoy_dev" / filepath
        if _corrected.exists():
            target = _corrected
    if not str(target.resolve()).startswith(str(base.resolve())):
        return jsonify({"success": False, "error": "路径越权"})

    _record_path_pattern(data.get('path', ''), str(target.relative_to(base)) if str(target).startswith(str(base)) else str(target), user_id, session_id)
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
    # 路径自动补全：command 中的路径缺少 clawsjoy_dev/ 前缀时，注入前缀
    _cmd = data.get("command", "")
    if "clawsjoy_dev/" not in _cmd and "/" in _cmd:
        _hint = f"cd clawsjoy_dev && {_cmd}"
        # 不修改原命令，在提示中标注
    path_obj = Path(dirpath)
    if path_obj.is_absolute() or str(dirpath).startswith("data/projects/"):
        target = path_obj
    else:
        # 从 agent_state 获取项目根目录
        project_root = "clawsjoy_dev"
        try:
            state_file = base / "clawsjoy_dev" / ".agent_state.json"
            if state_file.exists():
                try:

                    agent_state = json.loads(state_file.read_text())

                except:

                    agent_state = {}
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
    # 路径自动补全：ui/、services/、models/ 开头且不在项目子目录下时，自动补全
    _path_str = str(target)
    if not any(d in _path_str for d in ['youtube-autopilot/', 'exam-prep/']) and _path_str.startswith(('ui/', 'services/', 'models/')):
        # 从 world_model 获取项目根目录
        _state_file = base / "clawsjoy_dev" / ".agent_state.json"
        _proj_root = "youtube-autopilot"
        if _state_file.exists():
            try:
                _state = json.loads(_state_file.read_text())
                _wm = _state.get("world_model", {})
                _proj_root = _wm.get("project_root", "youtube-autopilot")
            except:
                pass
        target = base / _proj_root / filepath
    # 通用路径补全：如果路径不以 clawsjoy_dev/ 开头且不存在，尝试加前缀
    if not target.exists() and not str(dirpath).startswith("clawsjoy_dev/"):
        _corrected = base / "clawsjoy_dev" / filepath
        if _corrected.exists():
            target = _corrected
    if not str(target.resolve()).startswith(str(base.resolve())):
        return jsonify({"success": False, "error": "路径越权"})

    _record_path_pattern(data.get('path', ''), str(target.relative_to(base)) if str(target).startswith(str(base)) else str(target), user_id, session_id)
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
            # 索引文件为空，自动触发扫描
            _py_files = list(_project_dir.rglob("*.py"))
            _py_files = [f for f in _py_files if "test_" not in f.name and "/tests/" not in str(f) and not f.name.endswith(".bak")]
            for _pf in _py_files[:200]:
                try:
                    _code_indexer.index_file(str(_pf.relative_to(_project_dir)))
                except:
                    pass
            _code_indexer._save()
    if not _code_indexer._keyword_index:
        return jsonify({"success": False, "error": "代码索引尚未初始化，且未找到可索引的 Python 文件。"})
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
    import logging as _log
    import json as _json

    data = request.json or {}
    user_id = data.get("user_id", "default")
    session_id = data.get("session_id", "default")
    command = data.get("command", "")
    import logging as _log
    _log.getLogger('werkzeug').info(f'[EXEC_DEBUG] all keys: {list(data.keys())}, has_raw: {"raw_arguments" in data}')
    # P1: 如果前端传了 raw_arguments 但 command 为空，网关自己解析
    if not command and data.get("raw_arguments"):
        try:
            _args = _json.loads(data["raw_arguments"])
            command = _args.get("command", "")
        except Exception as _e:
            _log.getLogger('werkzeug').info(f'[EXEC_DEBUG] raw_arguments解析失败: {_e}, raw前200字符: {data["raw_arguments"][:200]}')

    cmd_name = command.split()[0] if command else ""
    if not command or not cmd_name:
        _log.getLogger('werkzeug').info(f'[EXEC_DEBUG] command为空或cmd_name为空: command={repr(command[:200])}, raw_keys={list(data.keys())}')
    
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
    # 路径自动补全：command 中的路径缺少 clawsjoy_dev/ 前缀时，注入前缀
    _cmd = data.get("command", "")
    if "clawsjoy_dev/" not in _cmd and "/" in _cmd:
        _hint = f"cd clawsjoy_dev && {_cmd}"
        # 不修改原命令，在提示中标注

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
        # 沙箱写入保护：拒绝修改沙箱外的文件
        _dangerous = False
        for _kw in (">", ">>", "tee ", "dd of=", "mkfs", "mount "):
            if _kw in command:
                _dangerous = True
                break
        if _dangerous:
            return jsonify({"success": False, "error": "禁止在沙箱外写入文件。所有修改操作必须在项目目录内进行。"})

        result = subprocess.run(command, shell=True, cwd=str(base),
                                capture_output=True, text=True, timeout=30)
        _hint = None
        if result.returncode != 0 and result.stderr and "No such file or directory" in result.stderr:
            import re as _re_path_hint
            _missing = _re_path_hint.findall(r"'([^']+)'", result.stderr)
            for _fp in _missing:
                if not _fp.startswith("clawsjoy_dev/"):
                    _full = base / "clawsjoy_dev" / _fp
                    if _full.exists():
                        _hint = f"路径缺少 clawsjoy_dev/ 前缀，正确路径: clawsjoy_dev/{_fp}"
                        break
        _resp = {
            "success": result.returncode == 0,
            "stdout": result.stdout[:2000],
            "stderr": result.stderr[:1000],
            "returncode": result.returncode
        }
        if _hint:
            _resp["hint"] = _hint
        return jsonify(_resp)
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
    
    global _consecutive_reads
    if not filepath:
        return jsonify({"success": False, "error": "path 必填"})
    # 写文件前重置连续读取计数器
    global _consecutive_reads
    _consecutive_reads = 0

    
    base = Path(f"data/projects/{user_id}/{session_id}")
    base.mkdir(parents=True, exist_ok=True)
    # 路径自动补全：command 中的路径缺少 clawsjoy_dev/ 前缀时，注入前缀
    _cmd = data.get("command", "")
    if "clawsjoy_dev/" not in _cmd and "/" in _cmd:
        _hint = f"cd clawsjoy_dev && {_cmd}"
        # 不修改原命令，在提示中标注
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
    # 路径自动补全：ui/、services/、models/ 开头且不在项目子目录下时，自动补全
    _path_str = str(target)
    if not any(d in _path_str for d in ['youtube-autopilot/', 'exam-prep/']) and _path_str.startswith(('ui/', 'services/', 'models/')):
        # 从 world_model 获取项目根目录
        _state_file = base / "clawsjoy_dev" / ".agent_state.json"
        _proj_root = "youtube-autopilot"
        if _state_file.exists():
            try:
                _state = json.loads(_state_file.read_text())
                _wm = _state.get("world_model", {})
                _proj_root = _wm.get("project_root", "youtube-autopilot")
            except:
                pass
        target = base / _proj_root / filepath
    # 通用路径补全：如果路径不以 clawsjoy_dev/ 开头且不存在，尝试加前缀
    if not target.exists() and not str(dirpath).startswith("clawsjoy_dev/"):
        _corrected = base / "clawsjoy_dev" / filepath
        if _corrected.exists():
            target = _corrected
    if not str(target.resolve()).startswith(str(base.resolve())):
        return jsonify({"success": False, "error": "路径越权"})

    _record_path_pattern(data.get('path', ''), str(target.relative_to(base)) if str(target).startswith(str(base)) else str(target), user_id, session_id)
    
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

def _compress_messages(messages, user_id, session_id="default", keep=30):
    if len(messages) <= keep:
        return messages
    from core.lib.context_manager import get_context
    ctx = get_context(user_id)
    if not hasattr(ctx, '_last_session_id') or ctx._last_session_id != session_id:
        ctx.clear()
        ctx._last_session_id = session_id
    system_msg = messages[0] if messages[0]["role"] == "system" else None
    # 保护任务目标：始终保留第一条 user 消息
    _first_user = None
    for _m in messages:
        if _m["role"] == "user":
            _first_user = _m
            break
    recent = messages[-keep:]
    old_messages = messages[1:-6] if system_msg else messages[:-6]
    summary = ctx.inject() or ""
    compressed = []
    if system_msg:
        compressed.append(system_msg)
    if summary:
        compressed.append({"role": "system", "content": f"【历史摘要】{summary}"})
    if _first_user and _first_user not in recent:
        compressed.append({"role": "system", "content": f"【任务目标】{_first_user['content'][:500]}"})
    compressed.extend(recent)
    return compressed


_file_retry_state = {}  # 按 session 存储的文件写入重试计数器

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
        try:
            try:

                state = json.loads(state_file.read_text())

            except:

                state = {}
        except:
            state = {}
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
    
    # 前置检测：目标文件是否已满足任务需求（v9_agent_chat 同步路径）
    if messages and messages[-1]["role"] == "user":
        _last_usr = messages[-1]["content"]
        import re as _re_pre2
        _write_kw2 = ['添加', '创建', '修改', '新增', '加入', '实现', '编写', '补充']
        if any(kw in _last_usr for kw in _write_kw2):
            _tgt = _re_pre2.search(r'[\w_]+/[\w_]+\.\w+', _last_usr)
            if _tgt:
                _tgt_file = _tgt.group(0)
                _base2 = Path(f"data/projects/{user_id}/{session_id}")
                _disk_paths2 = [
                    _base2 / _tgt_file,
                    _base2 / "clawsjoy_dev" / _tgt_file,
                ]
                _proj_dir = _base2 / "clawsjoy_dev"
                if _proj_dir.exists():
                    for _sd in _proj_dir.iterdir():
                        if _sd.is_dir() and not _sd.name.startswith(".") and _sd.name not in ("data", "code_index"):
                            _disk_paths2.append(_sd / _tgt_file)
                _found2 = None
                for _dp2 in _disk_paths2:
                    if _dp2.exists():
                        _found2 = _dp2
                        break
                if not _found2:
                    import glob as _glob2
                    _fname2 = _tgt_file.split("/")[-1]
                    _candidates2 = _glob2.glob(str(_base2 / "**" / _fname2), recursive=True)
                    for _c2 in _candidates2:
                        _cp2 = Path(_c2)
                        if _cp2.exists() and "resume-optimizer" in str(_cp2):
                            _found2 = _cp2
                            break
                    if not _found2:
                        for _c2 in _candidates2:
                            _cp2 = Path(_c2)
                            if _cp2.exists():
                                _found2 = _cp2
                                break
                if _found2:
                    try:
                        import ast as _ast_pre2
                        _fc = _found2.read_text()
                        if _found2.suffix == '.py':
                            _ast_pre2.parse(_fc)
                        _kw_raw2 = _re_pre2.sub(r'[^一-鿿a-zA-Z0-9]', ' ', _last_usr)
                        _kw2 = _re_pre2.findall(r'[一-鿿]{2,}|[a-zA-Z_]{3,}', _kw_raw2)
                        _noise2 = {'resume', 'optimizer', 'analysis_page', 'py', 'markdown', '文件', '点击后将', '分析结果导出为'}
                        _action_pre2 = {'添加', '创建', '修改', '删除', '新增', '加入', '实现', '编写', '补充', '完善', '中添加', '点击后', '分析结果导出', '点击后将分析结果导出为'}
                        _kw2 = [k for k in _kw2 if k.lower() not in _noise2 and k not in _action_pre2 and not (k.isascii() and k.isalpha())]
                        _matched2 = sum(1 for k in _kw2 if k.lower() in _fc.lower())
                        if _kw2 and _matched2 >= max(2, len(_kw2) * 0.5):
                            return jsonify({
                                "success": True,
                                "data": {"choices": [{"message": {"role": "assistant", "content": f"前置检测：文件已包含任务要求的功能（{', '.join(_kw2[:5])}），无需修改。"}}]}
                            })

                    except (SyntaxError, UnicodeDecodeError):
                        pass

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

        # 注入项目结构树
    _project_tree = _generate_project_tree(user_id, session_id)
    print(f"[PROJECT_TREE] len={len(_project_tree)}, preview={_project_tree[:100]}")
    if _project_tree:
        messages[0]["content"] += f"\n以下是从磁盘读取的实际项目文件结构：\n{_project_tree}"

    # 注入路径使用模式
    try:
        _state_file_p = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev/.agent_state.json")
        if _state_file_p.exists():
            _st = json.loads(_state_file_p.read_text())
            _pts = _st.get("known_patterns", [])
            if _pts:
                _corrections = [p for p in _pts if p.get("type") == "correction"]
                _successes = [p for p in _pts if p.get("type") == "success"]
                _hint = ""
                if _corrections:
                    _last_c = _corrections[-1]
                    _hint += f"路径修正提示：上次 '{_last_c['original']}' 自动补全为 '{_last_c['resolved']}'。所有路径需以 clawsjoy_dev/ 开头。"
                if _successes:
                    _hint += f" 最近 {len(_successes)} 次路径正确。"
                if _hint:
                    messages[0]["content"] += f"\n{_hint}"
    except:
        pass

    # 注入读取配额提示
    _last_usr_q = ""
    for _mq in messages:
        if _mq["role"] == "user":
            _last_usr_q = _mq["content"]
    _write_kw_q = ['创建', '修改', '添加', '新增', '写入', '实现', '编写', '补充']
    _is_write_q = any(kw in _last_usr_q for kw in _write_kw_q)
    _max_q = 5 if _is_write_q else 10
    messages[0]["content"] += f"\n读取配额：本次任务最多读取 {_max_q} 个文件，list_dir 最多 3 次。你可以从以下渠道获取信息而无需消耗配额：1) 上方项目树与磁盘实时同步，已列出所有文件路径，无需 list_dir 逐个确认 2) world_model 包含已写入文件的骨架 3) query_index 可查询代码结构（推荐用于查找目录内容，不消耗配额）。达到配额上限后 read_file 和 list_dir 将被拒绝，届时使用 query_index 获取信息，或基于已有信息直接写入交付。"

    # 多文件任务检测：追加规划模板
    import re as _re_plan
    _last_usr_plan = ""
    for _mp in messages:
        if _mp["role"] == "user":
            _last_usr_plan = _mp["content"]
    _file_matches = _re_plan.findall(r'[\w_]+/\w+\.py|[\w_]+\.py', _last_usr_plan)
    if len(_file_matches) >= 2:
        messages[0]["content"] += (
            "\n【多文件任务 — 请先列出执行计划】\n"
            "涉及文件: " + ", ".join(_file_matches[:8]) + "\n"
            "请按以下格式列出计划后，再执行修改:\n"
            "1. 修改文件: [文件路径]\n"
            "2. 修改内容: [具体改动]\n"
            "3. 执行顺序: [步骤]\n"
            "列出计划后等待确认，不要直接修改。"
        )

    # 新任务开始，清空 read_file 缓存，重置计数器
    global _consecutive_reads
    _read_cache.clear()
    _consecutive_reads = 0
    _consecutive_lists = 0
    
    # 从 .agent_state.json 注入 task_progress
    try:
        state_file = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev/.agent_state.json")
        if state_file.exists():
            try:

                agent_state = json.loads(state_file.read_text())

            except:

                agent_state = {}
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
            try:

                agent_state = json.loads(state_file.read_text())

            except:

                agent_state = {}
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
            
            # 首次使用：同步初始化索引（空项目直接跳过）
            if not index_file.exists():
                print(f"[V9] First use, initializing code index...")
                indexer.auto_init()
                indexer._save()
                # 不返回 initializing，空项目直接进入任务
            
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
    # ===== 预加载结束 =====

    # ★ 能力模型主动注入：根据任务类型从 world_model 提取模板
    try:
        _last_msg = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else ""
        _inject = None
        if any(kw in _last_msg for kw in ["创建", "新建", "添加"]) and any(kw in _last_msg for kw in ["ui/", "页面", "page"]):
            _inject = _get_skeletons_by_type("ui", user_id, session_id)
        elif any(kw in _last_msg for kw in ["创建", "新建", "添加"]) and any(kw in _last_msg for kw in ["services/", "服务", "service"]):
            _inject = _get_skeletons_by_type("services", user_id, session_id)
        elif any(kw in _last_msg for kw in ["创建", "新建", "添加"]) and any(kw in _last_msg for kw in ["models/", "模型", "model"]):
            _inject = _get_skeletons_by_type("models", user_id, session_id)
        if _inject:
            messages[0]["content"] += f"\n\n【参考模板 — 基于项目中已有文件骨架（与磁盘文件一致）】\n{_inject}"
    except:
        pass

    # Token 超限保护（在调 API 之前）
    if _estimate_tokens(messages) > MAX_CONTEXT_TOKENS * 0.8:
        # 分层压缩策略：根据 token 数动态调整
        _token_est = sum(len(str(m.get("content",""))) for m in messages) // 2
        if _token_est > 110000:
            # 极端情况：压缩到 15 条消息
            messages = _compress_messages(messages, user_id, session_id, keep=15)
            print(f"[V9] ⚠️ 上下文接近上限（{_token_est} tokens），已压缩至 {len(messages)} 条")
        elif _token_est > 80000:
            # 正常压缩：保留 30 条消息
            messages = _compress_messages(messages, user_id, session_id, keep=30)
            print(f"[V9] 上下文已压缩（{_token_est} tokens），剩余 {len(messages)} 条消息")
        else:
            print(f"[V9] 上下文 {_token_est} tokens，跳过压缩")

    # 构建 tools 定义
    tools = _get_agent_tools()

    # 构建 tools 之后
    if state_file.exists():
        try:
            try:

                state = json.loads(state_file.read_text())

            except:

                state = {}
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
        _thinking2 = False
        import re as _re_think
        _last_usr_think = ""
        for _mt in messages:
            if _mt["role"] == "user":
                _last_usr_think = _mt["content"]
        _file_think = _re_think.findall(r'[\w_]+/\w+\.py|[\w_]+\.py', _last_usr_think)
        _thinking2 = len(_file_think) >= 2
        resp = adapter.execute_with_tools(messages=messages, tools=tools, user_id=user_id, temperature=0.7, max_tokens=8000 if _thinking2 else 2000, thinking=_thinking2)

        if not resp.get("success"):
            return jsonify({"success": False, "error": resp.get("error", "API错误")})
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
        state = {}
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
                if reflection.get("task_pattern"):
                    state["last_task_pattern"] = reflection["task_pattern"]
                    
                # ★ 新增：意图提取
                last_assistant_msg = ""
                for m in reversed(messages):
                    if m["role"] == "assistant" and m.get("content"):
                        last_assistant_msg = m["content"]
                        break

                intent = _extract_intent(last_assistant_msg)
                if intent:
                    state["intent_model"] = intent
                
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
                try:

                    state = json.loads(state_file.read_text())

                except:

                    state = {}

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

            # 更新 last_task
            for _ml in messages:
                if _ml["role"] == "user":
                    state["last_task"] = _ml["content"][:200]
                    state["last_time"] = datetime.now().isoformat()
                    break

            _persist_state(state, state_file)
        except Exception as e:
            pass
        # 上下文管理器
        try:
            from core.lib.context_manager import get_context
            ctx = get_context(user_id)
            if not hasattr(ctx, '_last_session_id') or ctx._last_session_id != session_id:
                ctx.clear()
                ctx._last_session_id = session_id
            ctx.add_turn(last_user_msg, f"tokens={tokens}", "agent_workspace", {}, world_model=state.get("world_model"), last_task_pattern=state.get("last_task_pattern"), intent_model=state.get("intent_model"),)
        except:
            pass
        # ===== 学习能力结束 =====
        msg = data_resp.get("choices", [{}])[0].get("message", {})
        
        # 多文件任务硬约束：涉及2+文件时，必须先输出规划文本
        _last_usr_hard = ""
        for _mh in messages:
            if _mh["role"] == "user":
                _last_usr_hard = _mh["content"]
        import re as _re_hard
        _file_matches_hard = _re_hard.findall(r'[\w_]+/\w+\.py|[\w_]+\.py', _last_usr_hard)
        if len(_file_matches_hard) >= 2:
            _has_plan = bool(msg.get("content", "").strip())
            _tool_calls_raw = msg.get("tool_calls", [])
            _has_write = any(tc.get("function", {}).get("name") in ("write_file", "write_large") for tc in _tool_calls_raw)
            if not _has_plan:
                _files_list = ", ".join(_file_matches_hard[:8])
                _plan_msg = f"【系统】检测到多文件任务，请先列出执行计划再修改。\n涉及文件: {_files_list}\n\n请按以下格式列出计划:\n1. 修改文件: [路径]\n2. 修改内容: [具体改动]\n3. 执行顺序: [步骤]\n\n列出计划后，系统将自动放行后续修改操作。"
                messages.append({"role": "system", "content": _plan_msg})
                msg["content"] = ""
                # 不 return，让流程继续走到 DeepSeek 调用

        # ★ 网关拦截 write_file：长内容直接从 Agent 响应中提取并写入
        _tool_calls = msg.get("tool_calls", [])
        for _tc in _tool_calls:
            if _tc.get("function", {}).get("name") in ("write_file", "write_large"):
                try:
                    _args = json.loads(_tc["function"]["arguments"])
                    _content = _args.get("content", "")
                    _path = _args.get("path", "")
                    if _content and len(_content) > 3000 and _path:
                        # 重试计数：同一文件连续写入时检测完整性
                        _retry_key = f"retry_{_path}"
                        _retry_count = _file_retry_state.get(_retry_key, 0) + 1
                        _file_retry_state[_retry_key] = _retry_count
                        _base = Path(f"data/projects/{user_id}/{session_id}")
                        _base.mkdir(parents=True, exist_ok=True)
                        _target = _resolve_path(_base, _path)
                        _target.parent.mkdir(parents=True, exist_ok=True)
                        _target.write_text(_content, encoding='utf-8')
                        _update_world_model(str(_target), _content, user_id, session_id)
                        # 写入后自动语法检测
                        import subprocess as _sp2
                        _syntax_result = _sp2.run(
                            ['python3', '-c', f'compile(open("{_target}").read(), "{_target}", "exec")'],
                            capture_output=True, text=True, timeout=10
                        )
                        if _syntax_result.returncode != 0:
                            _args["content"] = f"[网关已写入但发现语法错误] {_syntax_result.stderr[:300]}\n请用 write_file 完整重写该文件，不要用 heredoc 逐段追加。"
                        else:
                            _defs = [l for l in _content.split('\n') if l.strip().startswith('def ')]
                            _classes = [l for l in _content.split('\n') if l.strip().startswith('class ')]
                            _summary = f"[长内容已由网关直接写入 {_target}，共 {len(_content)} 字符，{len(_classes)} 个类，{len(_defs)} 个方法，语法检查通过。"
                        if _retry_count >= 2:
                            _summary += f" 该文件已连续写入 {_retry_count} 次，禁止使用 heredoc。请用 write_file 一次性完整重写全部内容。"
                        else:
                            _summary += " 如果文件内容不完整，请用 write_file 完整重写，不要用 heredoc 追加。"
                            _args["content"] = _summary
                        _tc["function"]["arguments"] = json.dumps(_args, ensure_ascii=False)
                        # 超长内容 (>5000字符) 引导走临时文件通道
                        if len(_content) > 5000:
                            import uuid as _uuid2
                            _temp_name = f"agent_write_{_uuid2.uuid4().hex[:12]}.py"
                            _temp_path = Path(f"/tmp/clawsjoy_temp/{_temp_name}")
                            _temp_path.parent.mkdir(parents=True, exist_ok=True)
                            _temp_path.write_text(_content, encoding='utf-8')
                            _args["content"] = f"[超长内容已写入临时文件] 请调用 write_finalize(path=\'{_path}\', temp_path=\'{_temp_path}\') 完成写入。"
                            _tc["function"]["arguments"] = json.dumps(_args, ensure_ascii=False)
                except:
                    pass

        # ★ 交付物缺失检测：目标文件未写入 + 最近 3 次都是读取 → 注入信号
        import re as _re5
        _target_files = set()
        _last_user = messages[-1]["content"] if messages[-1]["role"] == "user" else ""
        _main_match = _re5.search(r'(?:修改|创建|完善|写入|新增|添加|生成|实现|编写|补充|新建|在)\s*[`"\']?([\w_]+/[\w_]+\.\w+)', _last_user)
        if _main_match:
            _target_files = {_main_match.group(1)}
        _written_files = set()
        for _m in messages:
            if _m["role"] == "assistant":
                for _tc in _m.get("tool_calls", []):
                    if _tc.get("function", {}).get("name") == "write_file":
                        try:
                            _args = json.loads(_tc["function"]["arguments"])
                            if "path" in _args:
                                _written_files.add(_args["path"])
                        except:
                            pass
        _assistant_msgs = [m for m in messages if m["role"] == "assistant"]
        _recent_actions = []
        for _am in _assistant_msgs[-3:]:
            for _tc in _am.get("tool_calls", []):
                _recent_actions.append(_tc["function"]["name"])
        if _target_files and not _target_files.issubset(_written_files):
            if _recent_actions and all(a in ("read_file", "list_dir", "search_files") for a in _recent_actions):
                _target_str = ", ".join(_target_files - _written_files)
                messages.append({"role": "system", "content": f"[系统] 目标文件 {_target_str} 尚未写入，但你最近 3 次操作都是读取。世界模型已包含文件结构信息，请直接 write_file 写入，不要继续读取。"})
        
        # 写入意图检测 v3：检测最后一轮是否只有读取、无写入/执行操作
        tool_calls = msg.get("tool_calls", [])
        READ_ONLY_TOOLS = {'read_file', 'list_dir', 'search_files', 'query_index'}
        WRITE_OR_EXEC_TOOLS = {'write_file', 'write_large', 'execute_command'}
        WRITE_KEYWORDS = ['创建', '修改', '完善', '写入', '新增', '添加文件', '生成', '实现', '编写', '补充', '新建', '写', '加', '改', '补全']
        user_msg = ""
        if messages:
            for m in reversed(messages):
                if m.get("role") == "user":
                    user_msg = m.get("content", "")
                    break
        if user_msg:
            has_write_intent = any(kw in user_msg for kw in WRITE_KEYWORDS)
            tool_names = {tc.get('function', {}).get('name') for tc in tool_calls} if tool_calls else set()
            is_read_only = (not tool_names) or tool_names.issubset(READ_ONLY_TOOLS)
            if has_write_intent and is_read_only:
                import re as _re
                path_match = _re.search(r'clawsjoy_dev/[\w/]+\.\w+', user_msg)
                target_path = path_match.group(0) if path_match else "目标文件"
                check_path = Path(f"data/projects/{user_id}/{session_id}") / target_path if path_match else None
                file_missing = check_path and not check_path.exists() if check_path else True
                if file_missing:
                    hint_msg = "[系统] 当前阶段：交付。请用 write_file 或 python3 heredoc 将修改写入文件。如果需要参考已有代码，直接写入后再用 read_file 验证。\n"
                    if msg.get("content"):
                        data_resp["choices"][0]["message"]["content"] = hint_msg + "\n\n" + msg["content"]
                    else:
                        data_resp["choices"][0]["message"]["content"] = hint_msg

        # 第四种防护：检测任务指令是否有对应的写入操作
        _action_words = ["重写", "修改", "创建", "添加", "修复", "实现", "完善", "增加", "删除", "更新"]
        _user_msgs = [m for m in messages if m["role"] == "user"]
        _last_user_msg = _user_msgs[-1]["content"] if _user_msgs else ""
        _has_action = any(w in _last_user_msg for w in _action_words)
        _has_write = any(
            tc["function"]["name"] == "write_file"
            for m in messages if m["role"] == "assistant"
            for tc in m.get("tool_calls", [])
        )
        if _has_action and not _has_write and data_resp.get("choices"):
            _target = _user_msgs[-1]["content"] if _user_msgs else ""
            import re as _re4
            _file_match = _re4.search(r'[\w/]+\.\w+', _target)
            _target_file = _file_match.group(0) if _file_match else "目标文件"
            data_resp["choices"][0]["message"]["content"] = (
                f"[系统] 检测到任务未执行：用户要求修改 {_target_file}，但未检测到 write_file 操作。\n"
                f"如果文件已包含所需功能，请回复\"已完成\"结束任务。\n"
                f"否则唯一可用操作：write_file(path='{_target_file}', content='完整文件内容')\n"
                f"禁止继续读取文件。请立即写入。"
            )

        # 更新 last_task
        try:
            _last_usr_v9 = ""
            for _mv9 in messages:
                if _mv9["role"] == "user":
                    _last_usr_v9 = _mv9["content"]
            if _last_usr_v9:
                _sf_v9 = Path(f"data/projects/{user_id}/{session_id}/clawsjoy_dev/.agent_state.json")
                _st_v9 = json.loads(_sf_v9.read_text()) if _sf_v9.exists() and _sf_v9.read_text().strip() else {}
                _st_v9["last_task"] = _last_usr_v9[:200]
                _st_v9["last_time"] = datetime.now().isoformat()
                _sf_v9.write_text(json.dumps(_st_v9, ensure_ascii=False, indent=2))
        except:
            pass

        return jsonify({"success": True, "data": data_resp, "tokens": tokens})
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


