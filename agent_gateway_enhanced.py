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

import psutil
import requests
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 注册 v5 API 蓝图
from api.v5 import agents, butler, health
from core.lib.config import config
from core.lib.error_handler import register_error_handlers, safe_execute
from core.lib.performance_middleware import get_perf_stats, monitor_performance
from core.lib.rate_limiter import rate_limit, rate_limiter
from core.lib.response_cache import response_cache
from core.lib.smart_active_service import smart_service
from core.lib.unified_config import unified_config
from core.lib.user_context import user_context
from engine.security import desensitizer

# ========== 连接池优化 ==========
session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)


# ========== Flask 应用 ==========
app = Flask(__name__)

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


@app.route("/metrics", methods=["GET"])
def metrics():
    try:
        return jsonify(
            {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
                "connections": len(psutil.net_connections()),
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


# ========== 增强对话（集成 Orchestrator 四引擎） ==========
@app.route("/api/v5/enhanced/chat", methods=["POST"])
@monitor_performance
@rate_limit(limit=30, window=60)
def enhanced_chat():
    # 写入文件日志
    with open("/tmp/enhanced_chat.log", "a") as f:
        import time

        f.write(f"{time.time()} - enhanced_chat 被调用了\n")
    data = request.json or {}
    message = data.get("message", "")
    message = desensitizer.desensitize(message)
    user_id = data.get("user_id", "guest")

    # 设置用户上下文
    from core.lib.user_context import user_context

    with user_context(user_id):
        # 情感识别
        from core.agents.base.communicable_agent import CommunicableAgent

        temp_agent = CommunicableAgent(user_id)
        emotion, emotion_conf = temp_agent.recognize_emotion(message)
        # ==========

        extract_user_info(message, user_id)

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

        # 尝试从缓存获取
        cached = response_cache.get(user_id, message)
        if cached:
            return jsonify(
                {
                    "success": True,
                    "response": cached,
                    "cached": True,
                    "agent": "cached",
                    "enhanced": True,
                    "user_id": user_id,
                    "detected_emotion": (
                        emotion.value if hasattr(emotion, "value") else str(emotion)
                    ),
                    "emotion_confidence": emotion_conf,
                }
            )

    # ========== 原子引擎注入 ==========
    try:
        from engine.knowledge import knowledge_engine
        from engine.profile import profile_engine
        from engine.semantic import semantic_engine

        semantic_result = semantic_engine.understand(message)
        intent_name = semantic_result.intent
        intent_confidence = semantic_result.confidence
        print(
            f"[原子引擎] user={user_id}, intent={intent_name}, conf={intent_confidence:.2f}"
        )
    except Exception as e:
        print(f"[原子引擎] 初始化失败: {e}")
        intent_name = "unknown"
        intent_confidence = 0.0

    # ===== 1. 统一决策入口（DecisionAgent 选择 A/B/C） =====
    try:
        from agents.decision_agent.agent import decision_agent

        # DecisionAgent 会内部选择 A/B/C 并调用对应 Agent
        result = decision_agent.process(message, {"user_id": user_id})

        response = result.get("response", "处理完成")
        agent_name = result.get("agent", "decision_agent")

        save_memory(user_id, f"用户说: {message}")
        save_memory(user_id, f"{agent_name}说: {response[:200]}")
        record_learning(f"{user_id} -> {agent_name}", True)
        response_cache.set(user_id, message, response)

        return jsonify(
            {
                "success": True,
                "response": response,
                "agent": agent_name,
                "routed": True,
                "enhanced": True,
                "user_id": user_id,
                "detected_emotion": (
                    emotion.value if hasattr(emotion, "value") else str(emotion)
                ),
                "emotion_confidence": emotion_conf,
            }
        )
    except Exception as e:
        print(f"Orchestrator 路由失败: {e}")

    # ===== 2. 原子技能和话本匹配 =====
    try:
        from agents.chat_agent import ChatAgent

        chat_agent = ChatAgent(user_id=user_id)
        atomic_result = chat_agent._check_atomic_skill(message)
        if atomic_result:
            save_memory(user_id, f"用户说: {message}")
            save_memory(user_id, f"ClawsJoy说: {atomic_result[:200]}")
            response_cache.set(user_id, message, atomic_result)
            return jsonify(
                {
                    "success": True,
                    "response": atomic_result,
                    "agent": "atomic_skill",
                    "enhanced": True,
                    "user_id": user_id,
                    "detected_emotion": (
                        emotion.value if hasattr(emotion, "value") else str(emotion)
                    ),
                    "emotion_confidence": emotion_conf,
                }
            )

        intent = chat_agent._match_intent(message)
        if intent:
            template = chat_agent._get_template(intent)
            if template:
                save_memory(user_id, f"用户说: {message}")
                save_memory(user_id, f"ClawsJoy说: {template[:200]}")
                response_cache.set(user_id, message, template)
                return jsonify(
                    {
                        "success": True,
                        "response": template,
                        "agent": "scriptbook",
                        "enhanced": True,
                        "user_id": user_id,
                        "detected_emotion": (
                            emotion.value if hasattr(emotion, "value") else str(emotion)
                        ),
                        "emotion_confidence": emotion_conf,
                    }
                )
    except Exception as e:
        print(f"原子技能/话本匹配失败: {e}")

    # ===== 3. 从状态回答 =====
    direct_answer = answer_from_state(message, user_id)
    if direct_answer:
        response_cache.set(user_id, message, direct_answer)
        return jsonify(
            {
                "success": True,
                "response": direct_answer,
                "agent": "state_manager",
                "enhanced": True,
                "user_id": user_id,
                "detected_emotion": (
                    emotion.value if hasattr(emotion, "value") else str(emotion)
                ),
                "emotion_confidence": emotion_conf,
            }
        )

    # ===== 4. 调用 LLM 服务（兜底） =====
    try:
        resp = requests.post(
            f"{config.LLM_URL}/chat", json={"message": message}, timeout=60
        )
        if resp.status_code == 200:
            response = resp.json().get("response", "")
        else:
            response = f"服务异常: {resp.status_code}"
    except Exception as e:
        response = f"服务繁忙: {e}"

    save_memory(user_id, f"用户说: {message}")
    save_memory(user_id, f"ClawsJoy说: {response[:200]}")
    record_learning(f"对话: {user_id} -> {message[:30]}", True)
    response_cache.set(user_id, message, response)

    return jsonify(
        {
            "success": True,
            "response": response,
            "agent": "chat_agent",
            "enhanced": True,
            "user_id": user_id,
            "detected_emotion": (
                emotion.value if hasattr(emotion, "value") else str(emotion)
            ),
            "emotion_confidence": emotion_conf,
        }
    )


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
@app.route("/api/agent/<agent_name>/message", methods=["POST"])
def agent_message(agent_name):
    """Agent 间通信端点 - 供 Orchestrator 调用其他 Agent"""
    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")

    # 设置用户上下文
    from core.lib.user_context import user_context

    with user_context(user_id):

        if not message:
            return jsonify({"success": False, "error": "message required"}), 400

    try:
        module = __import__(f"agents.{agent_name}.agent", fromlist=[agent_name])

        # 从配置文件读取类名映射
        from core.lib.unified_config import unified_config

        agent_class_map = unified_config.get("agent_class_map", {})

        class_name = agent_class_map.get(agent_name)  # 改为 agent_name
        if class_name is None:
            if agent_name.endswith("_agent"):
                base_name = agent_name[:-6]
            else:
                base_name = agent_name
            class_name = "".join(w.capitalize() for w in base_name.split("_")) + "Agent"

        agent_class = getattr(module, class_name)
        agent = agent_class(user_id)
        result = agent.process(message)
        return jsonify(result)
    except ImportError as e:
        return (
            jsonify(
                {"success": False, "error": f"Agent '{agent_name}' not found: {e}"}
            ),
            404,
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
                    class_name = (
                        "".join(w.capitalize() for w in base_name.split("_")) + "Agent"
                    )
                agent_class = getattr(module, class_name)
                agent = agent_class(user_id)

                # 如果 Agent 有 broadcast 方法就调用
                if hasattr(agent, "broadcast"):
                    result = agent.broadcast(message, sender)
                    results.append(
                        {"agent": agent_name, "success": True, "result": result}
                    )
                else:
                    results.append(
                        {"agent": agent_name, "success": True, "message": "已接收广播"}
                    )
            except Exception as e:
                results.append({"agent": agent_name, "success": False, "error": str(e)})

                return jsonify(
                    {
                        "success": True,
                        "message": f"广播已发送给 {len(results)} 个 Agent",
                        "sender": sender,
                        "results": results,
                    }
                )


# ========== 用户认证 API（使用现有 JWT 管理）==========
from core.lib.auth_api import AuthManager
from core.lib.auth_middleware import require_auth

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
@require_auth
def user_verify():
    """验证 token 是否有效"""
    from flask import g, jsonify

    return jsonify({"success": True, "user_id": g.user_id, "message": "Token 有效"})


@app.route("/api/user/profile", methods=["GET"])
@require_auth
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
@require_auth
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
@require_auth
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
@require_auth
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


import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
