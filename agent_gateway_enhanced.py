#!/usr/bin/env python3
"""ClawsJoy Gateway - 完整版主网关 v2.0

功能清单:
- 四引擎路由 (LLM → 向量 → 配置 → 规则)
- Agent 管理、技能管理
- 记忆系统、学习系统
- 向量系统、工作流系统
- 热重载系统、监控系统
- 俱乐部、管家、隐私保护
"""
import json
import os
import re
import sys
from datetime import datetime
from functools import lru_cache
from pathlib import Path

# ========== 安全保护模块（新增）==========
from core.lib.safety_guard import set_safe_recursion_limit

set_safe_recursion_limit()  # 设置递归深度限制为 5000
# ========== 日志配置 ==========
import logging

# =======================================
import psutil
import requests
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 注册 v5 API 蓝图
from api.v5 import agents, butler, health
from core.lib.auth_middleware import require_auth
from core.lib.chat_engine import chat_engine  # ✅ 直接使用单例
from core.lib.config import config
from core.lib.error_handler import register_error_handlers, safe_execute
from core.lib.performance_middleware import get_perf_stats, monitor_performance
from core.lib.rate_limiter import rate_limit, rate_limiter
from core.lib.response_cache import response_cache
from core.lib.smart_active_service import smart_service
from core.lib.unified_config import unified_config
from core.lib.user_context import user_context
from engine.security import desensitizer
from core.agents.wisdom.wisdom_factory import wisdom_factory
from core.agents.business.business_agent import BusinessAgent
from core.lib.json_standard import StandardJSON


# 配置日志级别
logging.basicConfig(
    level=logging.INFO,  # 生产环境用 INFO，调试用 DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/gateway.log"), logging.StreamHandler()],
)

# 抑制第三方库的 DEBUG 日志
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.info("🚀 ClawsJoy Gateway 启动中...")
# ==================================

# ========== 连接池优化 ==========
session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)


# ========== Flask 应用 ==========
app = Flask(__name__)


@app.route('/codex')
def codex():
    """Codex 风格代码助手界面"""
    from flask import render_template
    return render_template('codex.html')

# 注册全局错误处理器
register_error_handlers(app)
CORS(app)


# ========== 注册 v5 API 蓝图 ==========
app.register_blueprint(agents.api_bp, url_prefix="/api/v5")
app.register_blueprint(health.api_bp, url_prefix="/api/v5")
app.register_blueprint(butler.api_bp, url_prefix="/api/v5")


# ========== 简单缓存 ==========
class SimpleCache:
    def __init__(self, ttl=300):
        self.cache = {}
        self.ttl = ttl

    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now().timestamp() - timestamp < self.ttl:
                return data
            del self.cache[key]
        return None

    def set(self, key, value):
        self.cache[key] = (value, datetime.now().timestamp())

    def clear(self):
        self.cache.clear()


request_cache = SimpleCache(ttl=300)

# ========== 主动学习 ==========
try:
    from engine.active.integration import active_loop
except ImportError:

    class DummyActiveLoop:
        def process(self, **kwargs):
            return {}

    active_loop = DummyActiveLoop()


# ========== 数据目录 ==========
DATA_DIR = Path("data")
MEMORY_FILE = DATA_DIR / "memory_simple.json"
LEARNING_FILE = DATA_DIR / "learning_data" / "learning_stats.json"
MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "learning_data").mkdir(parents=True, exist_ok=True)


# ========== Gunicorn post_fork 钩子 ==========
def post_fork(server, worker):
    """每个 worker fork 后执行，重新启动监听器线程"""
    import os
    import sys

    sys.path.insert(0, os.getcwd())

    try:
        from core.lib.config_auto_watcher import config_auto_watcher

        config_auto_watcher.scan_and_register()
        config_auto_watcher.start()
        print(f"✅ Worker {worker.pid} 配置监听器已启动")
    except Exception as e:
        print(f"⚠️ Worker {worker.pid} 监听器启动失败: {e}")


# ========== 记忆函数 ==========
def load_memories(user_id):
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            all_memories = json.load(f)
            return all_memories.get(user_id, [])
    return []


def save_memory(user_id, fact):
    memories = load_memories(user_id)
    memories.append({"fact": fact, "timestamp": datetime.now().isoformat()})
    all_memories = {}
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            all_memories = json.load(f)
    all_memories[user_id] = memories[-100:]
    with open(MEMORY_FILE, "w") as f:
        json.dump(all_memories, f, indent=2)


def search_memories(user_id, query):
    memories = load_memories(user_id)
    results = []
    for m in memories:
        fact = m.get("fact", "")
        if "名字" in query and ("名字:" in fact or "叫" in fact):
            results.append(fact)
        elif query.lower() in fact.lower():
            results.append(fact)
    return results[:10]


# ========== 学习函数 ==========
def load_learning_stats():
    if LEARNING_FILE.exists():
        with open(LEARNING_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict):
                if "total_learnings" not in data:
                    data["total_learnings"] = data.get("learned", 0)
                return data
    return {"total_learnings": 0, "successful_learnings": 0, "failed_learnings": 0}


def record_learning(fact, success=True):
    stats = load_learning_stats()
    stats["total_learnings"] = stats.get("total_learnings", 0) + 1
    if success:
        stats["successful_learnings"] = stats.get("successful_learnings", 0) + 1
    else:
        stats["failed_learnings"] = stats.get("failed_learnings", 0) + 1
    with open(LEARNING_FILE, "w") as f:
        json.dump(stats, f, indent=2)


# ========== 用户状态 ==========
USER_STATES = {}


def get_user_state(user_id):
    if user_id not in USER_STATES:
        USER_STATES[user_id] = {}
    return USER_STATES[user_id]


def extract_user_info(message, user_id):

    # ========== 安全钩子检查 ==========
    from core.lib.security_hooks import SecurityHooks

    # 1. 输入清洗
    ok, message = True, message
    if not ok:
        return jsonify(
            {"success": False, "error": "输入包含非法字符", "enhanced": True}
        )

    # 2. 危险模式检测
    ok, error_msg = SecurityHooks.check_dangerous_patterns(message)
    if not ok:
        return jsonify(
            {
                "success": False,
                "error": error_msg,
                "response": f"⚠️ 检测到危险操作，已阻止: {error_msg}",
                "enhanced": True,
                "user_id": user_id,
            }
        )

    # 3. 频率限制
    ok, error_msg = SecurityHooks.check_rate_limit(
        user_id, {"max_requests_per_minute": 30}
    )
    if not ok:
        return jsonify(
            {
                "success": False,
                "error": error_msg,
                "response": error_msg,
                "enhanced": True,
                "user_id": user_id,
            }
        )

    state = get_user_state(user_id)
    name_match = re.search(r"我叫([\u4e00-\u9fa5]{2,4})", message)
    if name_match:
        name = name_match.group(1)
        state["name"] = name
        save_memory(user_id, f"用户名字: {name}")
        save_memory(user_id, f"用户说: 我叫{name}")
        return True
    return False


def answer_from_state(message, user_id):
    if "我叫什么名字" in message or "我的名字" in message:
        memories = load_memories(user_id)
        for m in memories:
            fact = m.get("fact", "")
            if "用户名字:" in fact:
                name = fact.replace("用户名字: ", "")
                if name:
                    return f"您叫{name}呀，我记着呢！"
            if "用户说: 我叫" in fact:
                start = fact.find("我叫")
                if start != -1:
                    name = fact[start + 2 : start + 6].strip("，。！？")
                    if name:
                        return f"您叫{name}呀，我记着呢！"
        return "您还没告诉我您的名字呢。您可以说'我叫XXX'告诉我哦~"
    return None


# ========== 基础路由 ==========
@app.route("/api/endpoints", methods=["GET"])
def list_endpoints():
    endpoints = []
    for rule in app.url_map.iter_rules():
        if not rule.rule.startswith("/static"):
            endpoints.append({"path": rule.rule, "methods": list(rule.methods)})
    return jsonify({"endpoints": endpoints, "total": len(endpoints)})


# ========== 统一监控指标（支持 JSON 和 Prometheus 格式） ==========
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

# 业务指标定义
request_count = Counter(
    "clawsjoy_requests_total", "Total requests", ["method", "endpoint", "status"]
)
request_duration = Histogram(
    "clawsjoy_request_duration_seconds", "Request duration", ["method", "endpoint"]
)
active_sessions = Counter("clawsjoy_active_sessions", "Active sessions")


@app.route("/metrics", methods=["GET"])
def metrics():
    """统一指标端点 - 根据 Accept 头返回 JSON 或 Prometheus 格式"""
    accept = request.headers.get("Accept", "")

    # Prometheus 格式
    if "text/plain" in accept or "prometheus" in accept:
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    # JSON 格式（默认）
    try:
        # 系统指标
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage("/").percent
        connections = len(psutil.net_connections())

        # 业务指标值
        requests_total = request_count._value.get()
        sessions_total = active_sessions._value.get()

        return jsonify(
            {
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "disk_usage": disk_usage,
                    "connections": connections,
                },
                "business": {
                    "requests_total": requests_total,
                    "active_sessions": sessions_total,
                },
                "status": "ok",
            }
        )
    except Exception as e:
        return (
            jsonify(
                {"status": "degraded", "error": str(e), "message": "部分指标不可用"}
            ),
            200,
        )


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {"status": "healthy", "service": "clawsjoy-gateway", "version": "5.0.0"}
    )


@app.route("/", methods=["GET"])
def index():
    return jsonify({"service": "ClawsJoy Gateway", "version": "5.0.0"})


# ========== 技能清单 ==========
@app.route("/api/skills/list", methods=["GET"])
def list_skills():
    try:
        from core.lib.unified_skill_manager import unified_manager

        skills = unified_manager.list_all()
        return jsonify({"success": True, "total": len(skills), "skills": skills})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ========== 技能执行 ==========
@app.route("/api/skills/execute", methods=["POST"])
def execute_skill():
    try:
        from core.lib.skill_loader_v3 import skill_loader

        data = request.json or {}
        skill_name = data.get("skill", "")
        params = data.get("params", {})
        if not skill_name:
            return jsonify({"success": False, "error": "skill required"}), 400
        result = skill_loader.execute(skill_name, params)
        return jsonify({"success": True, "result": result, "skill": skill_name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ========== 智能体 ==========
@app.route("/api/agents/list", methods=["GET"])
def list_agents():
    agents_list = [
        # 核心 Agent
        {"name": "orchestrator", "status": "active", "version": "2.0.0"},
        {"name": "chat_agent", "status": "active", "version": "2.0.0"},
        # 专业 Agent
        {"name": "code_agent", "status": "active", "version": "2.0.0"},
        {"name": "analysis_agent", "status": "active", "version": "2.0.0"},
        {"name": "decision_agent", "status": "active", "version": "2.0.0"},
        {"name": "translate_agent", "status": "active", "version": "2.0.0"},
        {"name": "dialect_agent", "status": "active", "version": "2.0.0"},
        {"name": "executor_agent", "status": "active", "version": "2.0.0"},
        {"name": "memory_agent", "status": "active", "version": "2.0.0"},
        {"name": "writer_agent", "status": "active", "version": "2.0.0"},
        {"name": "youtube_agent", "status": "active", "version": "2.0.0"},
        {"name": "video_agent", "status": "active", "version": "2.0.0"},
        {"name": "vision_agent", "status": "active", "version": "2.0.0"},
        {"name": "collaboration_agent", "status": "active", "version": "2.0.0"},
        {"name": "director_agent", "status": "active", "version": "2.0.0"},
        {"name": "calculator_agent", "status": "active", "version": "2.0.0"},
        {"name": "file_agent", "status": "active", "version": "1.0.0"},
        {"name": "video_indexer_agent", "status": "active", "version": "1.0.0"},
    ]
    return jsonify({"success": True, "total": len(agents_list), "agents": agents_list})


# ========== 模式识别查询 ==========
@app.route("/api/learning/patterns", methods=["GET"])
def get_patterns():
    try:
        from core.lib.pattern_recognizer import pattern_recognizer

        # 获取情感统计（如果有）
        emotion_stats = {}
        learning_file = Path("data/learning_data/learning_stats.json")
        if learning_file.exists():
            with open(learning_file, "r") as f:
                learning_data = json.load(f)
                emotion_stats = learning_data.get("emotion_stats", {})

        return jsonify(
            {
                "success": True,
                "stats": pattern_recognizer.get_stats(),
                "rules": pattern_recognizer.data.get("generated_rules", []),
                "emotion_stats": emotion_stats,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ========== Swagger API 文档 ==========
from flasgger import Swagger, swag_from

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

swagger = Swagger(app, config=swagger_config)

# 为现有的 enhanced_chat 添加文档（不要重新定义函数）
# 需要在原有的路由


# ========== 扩展原有 enhanced_chat 路由 ==========
# 注意：这是修改原有的路由，不是新增

@app.route("/api/v5/enhanced/chat", methods=["POST"])
@require_auth
def enhanced_chat():
    """增强对话接口 - 兼容旧格式 + 支持新格式"""
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("enhanced_chat 被调用")

    data = request.json or {}
    
    # 检测是否是标准化 JSON（包含 action 或 raw_input 字段）
    if "action" in data or "raw_input" in data:
        # 标准化 JSON：使用新的智慧处理
        user_id = data.get("user_id", "guest")
        agent_name = data.get("agent", "chat_agent")
        
        logger.info(f"标准化 JSON 输入: action={data.get('action')}, target={data.get('target')}")
        
        # 尝试使用智慧 Agent
        try:
            wisdom_agent = wisdom_factory.get_wisdom_agent(agent_name, user_id)
            if wisdom_agent:
                result = wisdom_agent.handle_json(data)
                return jsonify(result)
        except Exception as e:
            logger.error(f"智慧 Agent 处理失败: {e}")
        
        # 降级：使用原有 chat_engine
        from core.lib.chat_engine import chat_engine
        result = chat_engine.execute(data, user_id)
        return jsonify(result)
    
    else:
        # 普通文本输入
        message = data.get("message", "")
        user_id = data.get("user_id", "guest")
        
        logger.info(f"普通文本输入: {message[:50]}...")
        
        if not message:
            return jsonify({"success": False, "response": "请输入消息", "user_id": user_id})
        
        # 尝试使用智慧 Agent
        try:
            wisdom_agent = wisdom_factory.get_wisdom_agent("chat_agent", user_id)
            if wisdom_agent:
                result = wisdom_agent.process(message)
                return jsonify(result)
        except Exception as e:
            logger.error(f"智慧 Agent 处理失败: {e}")
        
        # 降级：使用原有 chat_engine
        from core.lib.chat_engine import chat_engine
        result = chat_engine.execute(message, user_id)
        return jsonify(result)





# ========== 记忆路由 ==========
@app.route("/api/v5/memory/remember", methods=["POST"])
def memory_remember():
    data = request.json or {}
    user_id = data.get("user_id", "guest")

    # 设置用户上下文
    from core.lib.user_context import user_context

    with user_context(user_id):
        fact = data.get("fact", "")
        if not fact:
            return jsonify({"success": False, "error": "fact required"}), 400
        save_memory(user_id, fact)
        record_learning(f"用户 {user_id} 学习了: {fact}", True)
        return jsonify({"success": True, "message": "记忆已存储"})


@app.route("/api/v5/memory/recall", methods=["POST"])
def memory_recall():
    data = request.json or {}
    user_id = data.get("user_id", "guest")

    # 设置用户上下文
    from core.lib.user_context import user_context

    with user_context(user_id):
        query = data.get("query", "")
        results = search_memories(user_id, query)
        return jsonify({"success": True, "results": results})


@app.route("/api/v5/memory/stats", methods=["GET"])
def memory_stats():
    user_id = request.args.get("user_id", "guest")
    memories = load_memories(user_id)
    return jsonify({"success": True, "total": len(memories)})


# ========== 学习路由 ==========
@app.route("/api/learning/stats", methods=["GET"])
def learning_stats():
    stats = load_learning_stats()
    return jsonify({"success": True, "stats": stats})


# ========== 扩展监控端点 ==========
@app.route("/api/v5/stats/cache", methods=["GET"])
def cache_stats():
    return jsonify(response_cache.get_stats())


@app.route("/api/v5/stats/performance", methods=["GET"])
def performance_stats():
    return jsonify(get_perf_stats())


@app.route("/api/v5/stats/ratelimit", methods=["GET"])
def ratelimit_stats():
    user_id = request.args.get("user_id")
    return jsonify(rate_limiter.get_stats(user_id))


# ========== 增强健康检查 ==========
@app.route("/api/v5/health/detailed", methods=["GET"])
def detailed_health():
    from core.lib.health_check import health_checker

    return jsonify(health_checker.check_all())


# ========== Agent 间通信 API ==========

from core.lib.input_validator import input_validator


@app.route("/api/agent/<agent_name>/message", methods=["POST"])
def agent_message(agent_name):
    """Agent 间通信端点 - 供 Orchestrator 调用其他 Agent"""
    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")

    # ========== 输入验证（新增） ==========
    validation = input_validator.validate_message(message)
    if not validation.valid:
        return (
            jsonify(
                {"success": False, "error": "输入验证失败", "errors": validation.errors}
            ),
            400,
        )

    # 使用清理后的消息
    clean_message = validation.sanitized_value
    # ========== 输入验证结束 ==========

    # 设置用户上下文
    from core.lib.user_context import user_context

    with user_context(user_id):
        # ✅ 修复：使用 clean_message 而不是 message
        if not clean_message:
            return jsonify({"success": False, "error": "message required"}), 400

    try:
        module = __import__(f"agents.{agent_name}.agent", fromlist=[agent_name])

        # 从配置文件读取类名映射
        from core.lib.unified_config import unified_config

        agent_class_map = unified_config.get("agent_class_map", {})

        class_name = agent_class_map.get(agent_name)
        if class_name is None:
            if agent_name.endswith("_agent"):
                base_name = agent_name[:-6]
            else:
                base_name = agent_name
            class_name = "".join(w.capitalize() for w in base_name.split("_")) + "Agent"

        agent_class = getattr(module, class_name)
        agent = agent_class(user_id)
        # ✅ 修复：使用 clean_message 而不是 message
        result = agent.process(clean_message)
        logger.info(f"返回结果: {result.get('response', '')[:100]}")
        return jsonify(result)

    except ImportError as e:
        return (
            jsonify(
                {"success": False, "error": f"Agent '{agent_name}' not found: {e}"}
            ),
            404,
        )
    except RecursionError as e:
        return (
            jsonify({"success": False, "error": "递归深度超限", "message": str(e)}),
            500,
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/debug/route", methods=["POST"])
def debug_route():
    from agents.decision_agent.agent import decision_agent

    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")

    # 设置用户上下文
    from core.lib.user_context import user_context

    with user_context(user_id):
        orchestrator = OrchestratorAgent(user_id)
        target = orchestrator.smart_route(message)
        return jsonify(
            {
                "message": message,
                "target": target,
                "orchestrator_used": str(orchestrator),
            }
        )


# 在 agent_gateway_enhanced.py 末尾添加
@app.route("/api/v5/audit/logs", methods=["GET"])
def get_audit_logs():
    user_id = request.args.get("user_id", "guest")
    from core.agents.base.communicable_agent import CommunicableAgent

    # 获取审计日志（需要实例）
    return jsonify({"logs": [], "message": "审计日志功能开发中"})


# ========== Agent 广播 API ==========
@app.route("/api/v5/agent/broadcast", methods=["POST"])
def agent_broadcast():
    """Agent 广播消息"""
    data = request.json or {}
    message = data.get("message", "")
    sender = data.get("sender", "system")
    user_id = data.get("user_id", "guest")

    # 设置用户上下文
    from core.lib.user_context import user_context

    with user_context(user_id):

        # 获取所有 Agent
        agent_names = [
            "code_agent",
            "chat_agent",
            "translate_agent",
            "dialect_agent",
            "analysis_agent",
            "decision_agent",
            "executor_agent",
            "memory_agent",
            "writer_agent",
            "youtube_agent",
            "video_agent",
            "vision_agent",
            "collaboration_agent",
            "director_agent",
            "calculator_agent",
            "file_agent",
        ]

        results = []
        for agent_name in agent_names:
            try:
                module = __import__(f"agents.{agent_name}.agent", fromlist=[agent_name])
                from core.lib.unified_config import unified_config

                agent_class_map = unified_config.get("agent_class_map", {})
                class_name = agent_class_map.get(agent_name)

                if class_name is None:
                    if agent_name.endswith("_agent"):
                        base_name = agent_name[:-6]
                    else:
                        base_name = agent_name
                    class_name = "".join(w.capitalize() for w in base_name.split("_")) + "Agent"
                
                agent_class = getattr(module, class_name)
                agent = agent_class(user_id)
                
                # 如果 Agent 有 broadcast 方法就调用
                if hasattr(agent, "broadcast"):
                    result = agent.broadcast(message, sender)
                    results.append({"agent": agent_name, "success": True, "result": result})
                else:
                    results.append({"agent": agent_name, "success": True, "message": "已接收广播"})
                    
            except Exception as e:
                results.append({"agent": agent_name, "success": False, "error": str(e)})
        
        # ✅ 注意：return 要放在 for 循环外面
        return jsonify({
            "success": True,
            "message": f"广播已发送给 {len(results)} 个 Agent",
            "sender": sender,
            "results": results,
        })




# ========== 用户认证 API（使用现有 JWT 管理）==========
from core.lib.auth_api import AuthManager

auth_manager = AuthManager()


@app.route("/api/user/register", methods=["POST"])
def user_register():
    """用户注册"""
    from flask import jsonify, request

    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    email = data.get("email", "")

    if not username or not password:
        return jsonify({"success": False, "error": "用户名和密码不能为空"}), 400

    result = auth_manager.register(username, password, role="user")

    if result.get("success"):
        # 同时创建用户加密目录（为 YouTube 凭证做准备）
        import json
        from pathlib import Path

        from core.lib.user_crypto import UserCrypto

        user_id = result.get("user_id")
        user_dir = Path(f"data/users/{username}")
        if not user_dir.exists():
            user_dir.mkdir(parents=True)

            # 创建所有必要子目录
            subdirs = [
                "encrypted",
                "communications/inbox",
                "communications/outbox",
                "communications/archive",
                "youtube_data",
                "scripts",
                "videos",
                "images",
                "logs",
                "workspace",
            ]
            for subdir in subdirs:
                (user_dir / subdir).mkdir(parents=True, exist_ok=True)

            # 创建 profile
            profile = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "role": "user",
                "created_at": __import__("datetime").datetime.now().isoformat(),
                "workspace": str(user_dir / "workspace"),
            }
            with open(user_dir / "profile.json", "w") as f:
                json.dump(profile, f, indent=2)

        print(f"✅ 用户注册成功: {username} ({user_id})")
        if not user_dir.exists():
            user_dir.mkdir(parents=True)
            (user_dir / "encrypted").mkdir()

            # 创建 profile
            profile = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "role": "user",
                "created_at": __import__("datetime").datetime.now().isoformat(),
            }
            with open(user_dir / "profile.json", "w") as f:
                json.dump(profile, f, indent=2)

    logger.info(f"返回结果: {result.get('response', '')[:100]}")
    return jsonify(result)


@app.route("/api/user/login", methods=["POST"])
def user_login():
    """用户登录 - 返回 JWT token"""
    from flask import jsonify, request

    from core.lib.auth_api import AuthManager

    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "error": "用户名和密码不能为空"}), 400

    auth = AuthManager()

    # 验证用户
    if username not in auth.users:
        return jsonify({"success": False, "error": "用户不存在"}), 401

    user = auth.users[username]
    if user["password_hash"] != auth._hash_password(password):
        return jsonify({"success": False, "error": "密码错误"}), 401

    # 生成 token
    token = auth._generate_token(user["user_id"], username, user.get("role", "user"))

    # 更新最后登录时间
    user["last_login"] = __import__("datetime").datetime.now().isoformat()
    auth._save_users()

    print(f"✅ 用户登录: {username}")

    return jsonify(
        {
            "success": True,
            "token": token,
            "user_id": user["user_id"],
            "username": username,
            "role": user.get("role", "user"),
        }
    )


@app.route("/api/user/verify", methods=["GET"])
# @require_auth
def user_verify():
    """验证 token 是否有效"""
    from flask import g, jsonify

    return jsonify({"success": True, "user_id": g.user_id, "message": "Token 有效"})


@app.route("/api/user/profile", methods=["GET"])
# @require_auth
def user_profile():
    """获取用户资料"""
    import json
    from pathlib import Path

    from flask import g, jsonify

    user_id = g.user_id

    # 查找用户目录
    for user_dir in Path("data/users").iterdir():
        profile_file = user_dir / "profile.json"
        if profile_file.exists():
            with open(profile_file, "r") as f:
                profile = json.load(f)
            if profile.get("user_id") == user_id:
                return jsonify({"success": True, "profile": profile})

    return jsonify({"success": False, "error": "用户资料不存在"}), 404


# ========== YouTube 凭证管理 API ==========
@app.route("/api/user/youtube/credentials", methods=["POST"])
# @require_auth
def set_youtube_credentials():
    """设置用户的 YouTube API 凭证"""
    from flask import g, jsonify, request

    from core.lib.user_crypto import UserCrypto

    data = request.get_json() or {}
    client_id = data.get("client_id", "").strip()
    client_secret = data.get("client_secret", "").strip()
    refresh_token = data.get("refresh_token", "").strip()

    if not client_id or not client_secret or not refresh_token:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "client_id, client_secret, refresh_token required",
                }
            ),
            400,
        )

    user_id = g.user_id

    # 获取用户密码（需要用户提供，用于加密）
    password = data.get("password", "").strip()
    if not password:
        return (
            jsonify({"success": False, "error": "password required for encryption"}),
            400,
        )

    try:
        crypto = UserCrypto(user_id, password)

        credentials = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "token_uri": "https://oauth2.googleapis.com/token",
        }

        crypto.encrypt(credentials, "youtube_credentials")

        print(f"✅ 用户 {user_id} YouTube 凭证已保存")

        return jsonify(
            {"success": True, "message": "YouTube credentials saved successfully"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/user/youtube/credentials", methods=["GET"])
# @require_auth
def get_youtube_credentials():
    """检查用户是否配置了 YouTube 凭证"""
    from flask import g, jsonify

    from core.lib.user_crypto import UserCrypto

    user_id = g.user_id
    password = request.args.get("password", "").strip()

    if not password:
        return jsonify({"success": False, "error": "password required"}), 400

    try:
        crypto = UserCrypto(user_id, password)
        creds = crypto.decrypt("youtube_credentials")

        if creds:
            return jsonify(
                {
                    "success": True,
                    "has_credentials": True,
                    "client_id": creds.get("client_id", "")[:20] + "...",
                }
            )
        else:
            return jsonify({"success": True, "has_credentials": False})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/user/youtube/channel", methods=["GET"])
# @require_auth
def get_youtube_channel():
    """获取用户的 YouTube 频道数据"""
    from flask import g, jsonify, request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    from core.lib.user_crypto import UserCrypto

    user_id = g.user_id
    password = request.args.get("password", "").strip()

    if not password:
        return jsonify({"success": False, "error": "password required"}), 400

    try:
        crypto = UserCrypto(user_id, password)
        creds_data = crypto.decrypt("youtube_credentials")

        if not creds_data:
            return (
                jsonify(
                    {"success": False, "error": "YouTube credentials not configured"}
                ),
                404,
            )

        creds = Credentials(
            token=None,
            refresh_token=creds_data.get("refresh_token"),
            token_uri=creds_data.get(
                "token_uri", "https://oauth2.googleapis.com/token"
            ),
            client_id=creds_data.get("client_id"),
            client_secret=creds_data.get("client_secret"),
        )

        youtube = build("youtube", "v3", credentials=creds)
        channel = (
            youtube.channels().list(part="statistics,snippet", mine=True).execute()
        )

        if channel.get("items"):
            stats = channel["items"][0]["statistics"]
            snippet = channel["items"][0]["snippet"]
            return jsonify(
                {
                    "success": True,
                    "channel": {
                        "title": snippet.get("title"),
                        "subscriber_count": stats.get("subscriberCount", 0),
                        "video_count": stats.get("videoCount", 0),
                        "view_count": stats.get("viewCount", 0),
                    },
                }
            )
        else:
            return jsonify({"success": False, "error": "No channel found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ======== 自我升级API ==========
import shutil
from pathlib import Path

from tools.real_log_collector import RealLogCollector

_collector = RealLogCollector()
from core.agents.builtin.config_upgrader import ConfigUpgrader

_upgrader = ConfigUpgrader(model_name="qwen2.5:7b")


@app.route("/api/v5/agents/<agent_name>/analyze", methods=["GET"])
def analyze_agent(agent_name):
    """分析Agent性能"""
    # TODO: 从你的日志系统获取真实日志
    logs = []  # 替换为真实日志收集
    result = _upgrader.analyze_performance(agent_name, logs)
    logger.info(f"返回结果: {result.get('response', '')[:100]}")
    return jsonify(result)


@app.route("/api/v5/agents/<agent_name>/upgrade", methods=["POST"])
def upgrade_agent(agent_name):
    """手动触发Agent升级"""
    data = request.json or {}
    auto_apply = data.get("auto_apply", False)

    # 收集真实日志（需要实现）
    logs = []  # TODO: 从日志系统收集

    result = _upgrader.upgrade_agent(agent_name, logs, auto_apply=auto_apply)
    logger.info(f"返回结果: {result.get('response', '')[:100]}")
    return jsonify(result)


@app.route("/api/v5/admin/upgrade/status", methods=["GET"])
def get_upgrade_status():
    """获取升级系统状态"""
    return jsonify(
        {
            "total_upgrades": len(_upgrader.history),
            "last_upgrade": _upgrader.history[-1] if _upgrader.history else None,
            "agents_monitored": ["chat_agent", "code_agent", "vision_agent"],
        }
    )


@app.route("/api/v5/admin/upgrade/now/<agent_name>", methods=["POST"])
def trigger_upgrade(agent_name):
    """手动触发升级"""
    logs = _collector.collect_agent_logs(agent_name, hours=24)
    result = _upgrader.upgrade_agent(agent_name, logs, auto_apply=True)
    logger.info(f"返回结果: {result.get('response', '')[:100]}")
    return jsonify(result)


@app.route("/api/v5/admin/upgrade/rollback/<agent_name>", methods=["POST"])
def rollback_upgrade(agent_name):
    """回滚到上一个配置"""
    config_file = Path(f"agents/{agent_name}/config.yaml")
    backup_file = config_file.with_suffix(".yaml.bak")

    if backup_file.exists():
        shutil.copy2(backup_file, config_file)
        return jsonify({"success": True, "message": f"{agent_name} 已回滚"})
    return jsonify({"success": False, "message": "没有找到备份文件"})


@app.route("/api/v5/admin/upgrade/history", methods=["GET"])
def get_upgrade_history_admin():
    """获取升级历史"""
    return jsonify(
        {"history": _upgrader.history[-50:], "total": len(_upgrader.history)}
    )


# ========== 引擎管理 API ==========
@app.route("/api/v5/admin/engine/chat/status", methods=["GET"])
# @require_auth
def get_chat_engine_status():
    """获取对话引擎状态"""

    return jsonify(chat_engine.get_status())


@app.route("/api/v5/admin/engine/chat/enable", methods=["POST"])
# @require_auth
def enable_chat_engine():
    """启用对话引擎"""

    chat_engine.enabled = True
    return jsonify(
        {
            "success": True,
            "message": "对话引擎已启用",
            "status": chat_engine.get_status(),
        }
    )


@app.route("/api/v5/admin/engine/chat/disable", methods=["POST"])
# @require_auth
def disable_chat_engine():
    """禁用对话引擎"""

    chat_engine.enabled = False
    return jsonify(
        {
            "success": True,
            "message": "对话引擎已禁用",
            "status": chat_engine.get_status(),
        }
    )


@app.route("/api/v5/admin/engine/chat/config", methods=["POST"])
# @require_auth
def config_chat_engine():
    """配置对话引擎"""

    data = request.json or {}
    chat_engine.update_config(data)
    return jsonify(
        {
            "success": True,
            "message": "引擎配置已更新",
            "status": chat_engine.get_status(),
        }
    )


@app.route("/api/v5/chat/stream", methods=["POST"])
@require_auth
def chat_stream():
    """流式对话接口"""
    import json

    import requests
    from flask import Response, stream_with_context

    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")

    def generate():
        try:
            resp = requests.post(
                "http://localhost:5012/chat/stream",
                json={"message": message},
                stream=True,
                timeout=60,
            )

            for line in resp.iter_lines():
                if line:
                    yield f"{line.decode()}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route("/api/v5/feedback", methods=["POST"])
def submit_feedback():
    """收集用户反馈"""
    data = request.json or {}
    feedback = data.get("feedback", "")
    rating = data.get("rating", 0)
    user_id = data.get("user_id", "anonymous")
    
    from pathlib import Path
    import json
    from datetime import datetime
    
    feedback_file = Path("data/feedback.json")
    
    # 读取现有数据
    if feedback_file.exists():
        with open(feedback_file, 'r') as f:
            all_feedback = json.load(f)
    else:
        all_feedback = {"success": [], "failure": []}
    
    # 添加反馈到对应类别
    if rating >= 4:
        category = "success"
    else:
        category = "failure"
    
    all_feedback[category].append({
        "user_id": user_id,
        "feedback": feedback,
        "rating": rating,
        "timestamp": datetime.now().isoformat()
    })
    
    with open(feedback_file, 'w') as f:
        json.dump(all_feedback, f, indent=2)
    
    return jsonify({"success": True, "message": "感谢您的反馈！"})



@app.route('/web/<path:filename>')
def serve_web(filename):
    from flask import send_from_directory
    return send_from_directory('web', filename)

@app.route('/web')
def web_index():
    from flask import send_from_directory
    return send_from_directory('web', 'index.html')


@app.route('/api/v5/image/generate', methods=['POST'])
def generate_image():
    """文生图接口"""
    from flask import request, jsonify
    from core.lib.free_image_api import free_api

    data = request.json or {}
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({'error': '请提供提示词'}), 400

    result = free_api.get_image_url(prompt)
    return jsonify(result)




# ========== 新增智慧对话路由（不影响现有接口）==========

@app.route("/api/v5/wisdom/chat", methods=["POST"])
@swag_from({
    'tags': ['智慧对话'],
    'summary': '智慧对话接口',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'string', 'description': '用户ID'},
                    'agent': {'type': 'string', 'description': 'Agent名称', 'default': 'chat_agent'},
                    'message': {'type': 'string', 'description': '消息内容'},
                }
            }
        }
    ],
    'responses': {
        '200': {'description': '成功'},
        '404': {'description': 'Agent不存在'},
        '500': {'description': '服务器错误'}
    }
})
def wisdom_chat():
    """
    智慧对话接口 - 新接口，独立于原有 enhanced_chat - 带请求验证

    特点:
    1. 支持标准化 JSON 输入
    2. 支持自然语言输入
    3. 自动路由到合适的 Agent
    4. 带缓存和智慧能力
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"success": False, "response": "无效的JSON格式"}), 400
    except Exception as e:
        return jsonify({"success": False, "response": f"JSON解析错误: {str(e)}"}), 400
    
    user_id = data.get("user_id", "guest")
    message = data.get("message", "")
    agent_name = data.get("agent", "chat_agent")
    
    # 验证必要字段
    if not message:
        return jsonify({"success": False, "response": "消息不能为空"}), 400
    
    # 限制消息长度
    if len(message) > 1000:
        return jsonify({"success": False, "response": "消息过长，请控制在1000字符以内"}), 400
    
    # 过滤特殊字符（防止注入）
    import re
    if re.search(r'[<>]', message):
        message = re.sub(r'[<>]', '', message)
    # ... 原有逻辑 ...

    # 检测输入类型
    if "action" in data or "raw_input" in data:
        # 标准化 JSON 输入
        agent_name = data.get("agent", "chat_agent")
        wisdom_agent = wisdom_factory.get_wisdom_agent(agent_name, user_id)

        if not wisdom_agent:
            return jsonify({
                "version": "1.1",
                "success": False,
                "error": f"Agent {agent_name} 不可用",
                "output_content": f"❌ Agent {agent_name} 不可用"
            })

        result = wisdom_agent.handle_json(data)
        return jsonify(result)
    else:
        # 自然语言输入 - 使用请求中指定的 agent，默认为 chat_agent
        agent_name = data.get("agent", "chat_agent")
        wisdom_agent = wisdom_factory.get_wisdom_agent(agent_name, user_id)

        if not wisdom_agent:
            return jsonify({"success": False, "response": f"Agent {agent_name} 不可用"})

        result = wisdom_agent.process(message)
        return jsonify(result)


# ========== 新增决策统计接口 ==========

@app.route("/api/v5/wisdom/decision/stats", methods=["GET"])
@swag_from('docs/swagger/decision_stats.yml')  # 添加这行
def wisdom_decision_stats():
    """获取决策者学习统计"""
    user_id = request.args.get("user_id", "guest")
    
    decision_agent = wisdom_factory.get_wisdom_agent("decision_agent", user_id)
    
    if not decision_agent:
        return jsonify({"error": "DecisionAgent 未加载"}), 404
    
    if hasattr(decision_agent, 'get_learning_stats'):
        stats = decision_agent.get_learning_stats()
        return jsonify({
            "success": True,
            "stats": stats,
            "user_id": user_id
        })
    
    return jsonify({"error": "DecisionAgent 不支持学习统计"}), 400


@app.route("/api/v5/wisdom/decision/feedback", methods=["POST"])
@swag_from('docs/swagger/decision_feedback.yml')
def wisdom_decision_feedback():
    """提供决策反馈（用于学习）"""
    data = request.json or {}
    user_id = data.get("user_id", "guest")
    task_id = data.get("task_id")
    was_correct = data.get("was_correct", False)
    correct_agent = data.get("correct_agent", None)
    
    decision_agent = wisdom_factory.get_wisdom_agent("decision_agent", user_id)
    
    if not decision_agent:
        return jsonify({"error": "DecisionAgent 未加载"}), 404
    
    if hasattr(decision_agent, 'provide_feedback'):
        result = decision_agent.provide_feedback(task_id, was_correct, correct_agent)
        return jsonify(result)
    
    return jsonify({"error": "DecisionAgent 不支持反馈"}), 400


@app.route("/api/v5/wisdom/decision/history", methods=["GET"])
@swag_from('docs/swagger/decision_history.yml')
def wisdom_decision_history():
    """获取决策历史"""
    user_id = request.args.get("user_id", "guest")
    limit = int(request.args.get("limit", 50))
    
    decision_agent = wisdom_factory.get_wisdom_agent("decision_agent", user_id)
    
    if not decision_agent:
        return jsonify({"error": "DecisionAgent 未加载"}), 404
    
    if hasattr(decision_agent, '_decision_history'):
        history = decision_agent._decision_history[-limit:]
        return jsonify({
            "success": True,
            "history": history,
            "total": len(decision_agent._decision_history),
            "user_id": user_id
        })
    
    return jsonify({"error": "无法获取决策历史"}), 400


# ========== 新增智慧统计接口 ==========

@app.route("/api/v5/wisdom/stats", methods=["GET"])
@swag_from('docs/swagger/wisdom_stats.yml')
def wisdom_stats():
    """获取智慧 Agent 统计信息"""
    user_id = request.args.get("user_id", "guest")
    agent_name = request.args.get("agent", None)
    
    if agent_name:
        wisdom_agent = wisdom_factory.get_wisdom_agent(agent_name, user_id)
        if wisdom_agent:
            return jsonify(wisdom_agent.get_self_awareness())
        return jsonify({"error": f"Agent {agent_name} 不存在或未激活"}), 404
    
    return jsonify(wisdom_factory.get_all_wisdom_stats())


# ========== 新增决策解释接口 ==========

@app.route("/api/v5/wisdom/explain", methods=["POST"])
@swag_from('docs/swagger/wisdom_explain.yml')
def wisdom_explain():
    """解释 Agent 的决策过程"""
    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")
    agent_name = data.get("agent", "chat_agent")
    
    wisdom_agent = wisdom_factory.get_wisdom_agent(agent_name, user_id)
    
    if not wisdom_agent:
        return jsonify({"error": f"Agent {agent_name} 不存在"}), 404
    
    explanation = wisdom_agent.explain_decision(message)
    return jsonify(explanation)


# ========== 新增热重载接口 ==========

@app.route("/api/v5/wisdom/reload", methods=["POST"])
@swag_from('docs/swagger/wisdom_reload.yml')
def wisdom_reload():
    """热重载指定 Agent"""
    data = request.json or {}
    agent_name = data.get("agent")
    
    if not agent_name:
        return jsonify({"error": "请指定 agent 名称"}), 400
    
    # 清除缓存，下次访问时会重新加载
    if agent_name in wisdom_factory._wrapped_agents:
        del wisdom_factory._wrapped_agents[agent_name]
        return jsonify({"success": True, "message": f"Agent {agent_name} 已热重载"})
    
    return jsonify({"success": False, "message": f"Agent {agent_name} 未加载"}), 404


# ========== Agent 列表 API ==========
@app.route("/api/v5/agent/list", methods=["GET"])
@swag_from('docs/swagger/agent_list.yml')
def agent_list():
    """列出所有已注册的 Agent"""
    from core.lib.agent_registry import agent_registry
    return jsonify({
        "success": True,
        "agents": agent_registry.list_all(),
        "stats": agent_registry.get_stats()
    })

# ========== 话本管理 API ==========

@app.route("/api/v5/scriptbook/stats", methods=["GET"])
def scriptbook_stats():
    """获取话本统计"""
    agent_name = request.args.get("agent", "chat_agent")
    
    from core.lib.scriptbook_learner import scriptbook_learner
    # 重新初始化指定 agent 的学习器
    scriptbook_learner.agent_name = agent_name
    scriptbook_learner._load_stats()
    
    stats = scriptbook_learner.get_stats()
    return jsonify({
        "success": True,
        "agent": agent_name,
        "stats": stats
    })


@app.route("/api/v5/scriptbook/optimize", methods=["POST"])
def scriptbook_optimize():
    """触发话本优化"""
    data = request.json or {}
    agent_name = data.get("agent", "chat_agent")
    auto_apply = data.get("auto_apply", False)
    
    from core.lib.scriptbook_learner import scriptbook_learner
    scriptbook_learner.agent_name = agent_name
    scriptbook_learner._load_stats()
    
    stats = scriptbook_learner.get_stats()
    suggestions = stats.get("suggestions", [])
    
    result = {
        "success": True,
        "agent": agent_name,
        "hit_rate": stats["hit_rate"],
        "suggestions": suggestions
    }
    
    if auto_apply and suggestions:
        # 自动应用建议
        result["auto_applied"] = _apply_scriptbook_suggestions(agent_name, suggestions)
    
    return jsonify(result)


@app.route("/api/v5/scriptbook/update", methods=["POST"])
def scriptbook_update():
    """手动更新话本"""
    data = request.json or {}
    agent_name = data.get("agent", "chat_agent")
    intent = data.get("intent")
    keywords = data.get("keywords", [])
    template = data.get("template")
    
    if not intent or not template:
        return jsonify({"success": False, "error": "intent and template required"}), 400
    
    # 更新话本文件
    import yaml
    from pathlib import Path
    
    script_path = Path(f"agents/{agent_name}/scriptbook.yaml")
    if not script_path.exists():
        script_path = Path(f"config/butler/scriptbook.yaml")
    
    if script_path.exists():
        with open(script_path, 'r') as f:
            config = yaml.safe_load(f) or {}
        
        # 添加新意图
        if "intents" not in config:
            config["intents"] = []
        
        config["intents"].append({
            "keywords": keywords,
            "response": intent
        })
        
        if "templates" not in config:
            config["templates"] = {}
        config["templates"][intent] = template
        
        with open(script_path, 'w') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        return jsonify({"success": True, "message": f"话本已更新: {intent}"})
    
    return jsonify({"success": False, "error": "话本文件不存在"}), 404


def _apply_scriptbook_suggestions(agent_name: str, suggestions: list) -> list:
    """自动应用话本建议"""
    applied = []
    for sug in suggestions:
        # 生成新话本
        new_intent = f"auto_{sug['type']}"
        keywords = sug.get("suggested_keywords", [])
        template = f"用户说了「{'」、「'.join(keywords)}」之类的话，需要友好回应。"
        
        # 更新话本
        import yaml
        from pathlib import Path
        
        script_path = Path(f"agents/{agent_name}/scriptbook.yaml")
        if script_path.exists():
            with open(script_path, 'r') as f:
                config = yaml.safe_load(f) or {}
            
            if "intents" not in config:
                config["intents"] = []
            
            # 避免重复
            existing = [i.get("response") for i in config["intents"]]
            if new_intent not in existing:
                config["intents"].append({
                    "keywords": keywords,
                    "response": new_intent
                })
                config["templates"][new_intent] = template
                
                with open(script_path, 'w') as f:
                    yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
                
                applied.append(new_intent)
    
    return applied


@app.route("/api/v5/scriptbook/hot-reload", methods=["POST"])
def scriptbook_hot_reload():
    """热重载话本"""
    agent_name = request.json.get("agent", "chat_agent")
    
    # 清除缓存，重新加载
    from core.agents.wisdom.wisdom_factory import wisdom_factory
    wisdom_agent = wisdom_factory.get_wisdom_agent(agent_name, "system")
    
    if wisdom_agent and hasattr(wisdom_agent, '_load_scriptbook'):
        wisdom_agent._load_scriptbook()
        return jsonify({"success": True, "message": f"话本已热重载: {agent_name}"})
    
    return jsonify({"success": False, "error": "Agent 不支持话本热重载"}), 400


# ========== Prompt 升级 API ==========

@app.route("/api/v5/prompt/stats", methods=["GET"])
def prompt_stats():
    """获取 Prompt 升级统计"""
    agent_name = request.args.get("agent", "chat_agent")
    
    from core.lib.prompt_upgrader import get_prompt_upgrader
    upgrader = get_prompt_upgrader(agent_name)
    
    return jsonify({
        "success": True,
        "agent": agent_name,
        "stats": upgrader.get_stats()
    })


@app.route("/api/v5/prompt/upgrade", methods=["POST"])
def prompt_upgrade():
    """手动触发 Prompt 升级"""
    agent_name = request.json.get("agent", "chat_agent")
    
    from core.lib.prompt_upgrader import get_prompt_upgrader
    upgrader = get_prompt_upgrader(agent_name)
    upgrader._generate_new_version()
    
    return jsonify({
        "success": True,
        "message": f"已触发 {agent_name} Prompt 升级",
        "current_version": upgrader.current_version,
        "test_version": upgrader.test_version
    })



# ========== 启动入口 ==========
if __name__ == "__main__":
    port = unified_config.get("services.gateway.port", 5002)
    smart_service.start()
    # HookManager 是单例，自动初始化
    from core.lib.hook_manager import HookManager

    HookManager()  # 触发初始化
    print("=" * 50)
    print(f"🚀 ClawsJoy Gateway 完整版启动在端口 {port}")
    print(f"   Workers: 4, Threads: 8, 并发: 32")
    print("=" * 50)
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)

# ========== 事件触发重试机制 ==========
# 用户不满意时，可以通过以下方式触发重试：
# POST /api/event/retry
# {
#   "task_id": "xxx",
#   "user_id": "user1",
#   "feedback": "需要更详细的趋势分析"
# }


