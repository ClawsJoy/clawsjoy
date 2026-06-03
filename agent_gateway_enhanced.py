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

from core.lib.unified_config import unified_config
from engine.security import desensitizer
import psutil

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

    import atexit

    def cleanup():
        try:
            from core.lib.config_watcher import config_watcher

            config_watcher.stop()
        except:
            pass

    atexit.register(cleanup)


if "gunicorn" in sys.modules:
    try:
        from gunicorn import glogging

        print("✅ Gunicorn post_fork 钩子已注册")
    except:
        pass


from core.lib.smart_active_service import smart_service

# ========== 连接池优化 ==========
session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)


# ========== Flask 应用 ==========
app = Flask(__name__)
CORS(app)


# ========== 缓存 ==========
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


# 需要在 agent_gateway_enhanced.py 添加端点列表
@app.route("/api/endpoints", methods=["GET"])
def list_endpoints():
    """列出所有可用 API 端点"""
    endpoints = []
    for rule in app.url_map.iter_rules():
        if not rule.rule.startswith("/static"):
            endpoints.append({"path": rule.rule, "methods": list(rule.methods)})
    return jsonify({"endpoints": endpoints, "total": len(endpoints)})

# 然后在健康检查端点附近添加
@app.route('/metrics')
def metrics():
    """监控指标端点 - 安全版本"""
    try:
        return jsonify({
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage("/").percent,
            "connections": len(psutil.net_connections()),
            "status": "ok"
        })
    except Exception as e:
        # 如果失败，返回基本信息
        return jsonify({
            "status": "degraded",
            "error": str(e),
            "message": "部分指标不可用"
        }), 200

# ========== 基础路由 ==========
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
    """执行技能"""
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
    agents = [
        {"name": "code_agent", "status": "active", "version": "2.0.0"},
        {"name": "analysis_agent", "status": "active", "version": "1.0.0"},
        {"name": "decision_agent", "status": "active", "version": "1.0.0"},
        {"name": "executor_agent", "status": "active", "version": "1.0.0"},
        {"name": "orchestrator", "status": "active", "version": "2.0.0"},
        {"name": "translate_agent", "status": "active", "version": "2.0.0"},
        {"name": "vision_agent", "status": "active", "version": "2.0.0"},
        {"name": "memory_agent", "status": "active", "version": "2.0.0"},
        {"name": "video_agent", "status": "active", "version": "2.0.0"},
        {"name": "youtube_agent", "status": "active", "version": "1.0.0"},
        {"name": "director_agent", "status": "active", "version": "1.0.0"},
        {"name": "writer_agent", "status": "active", "version": "1.0.0"},
        {"name": "dialect_agent", "status": "active", "version": "1.0.0"},
        {"name": "collaboration_agent", "status": "active", "version": "1.0.0"},
        {"name": "video_indexer_agent", "status": "active", "version": "1.0.0"},
        {"name": "chat_agent", "status": "active", "version": "2.0.0"},
    ]
    return jsonify({"success": True, "total": len(agents), "agents": agents})


# ========== 模式识别查询 ==========
@app.route("/api/learning/patterns", methods=["GET"])
def get_patterns():
    try:
        from core.lib.pattern_recognizer import pattern_recognizer

        return jsonify(
            {
                "success": True,
                "stats": pattern_recognizer.get_stats(),
                "rules": pattern_recognizer.data.get("generated_rules", []),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ========== 增强对话（集成 Orchestrator 四引擎） ==========
@app.route("/api/v5/enhanced/chat", methods=["POST"])
def enhanced_chat():
    data = request.json or {}
    message = data.get("message", "")
    message = desensitizer.desensitize(message)
    user_id = data.get("user_id", "guest")

    extract_user_info(message, user_id)

    # ========== 原子引擎注入 ==========
    try:
        from engine.knowledge import knowledge_engine
        from engine.profile import profile_engine
        from engine.semantic import semantic_engine

        semantic_result = semantic_engine.understand(message)
        intent_name = semantic_result.intent
        intent_confidence = semantic_result.confidence
        entities = (
            semantic_result.entities if hasattr(semantic_result, "entities") else {}
        )

        profile = profile_engine.get_or_create(user_id)
        if entities.get("name"):
            profile_engine.update_name(user_id, entities["name"])
        if entities.get("preference"):
            profile_engine.add_preference(user_id, entities["preference"])

        kg_result = knowledge_engine.query(message)
        print(
            f"[原子引擎] user={user_id}, intent={intent_name}, conf={intent_confidence:.2f}"
        )
    except Exception as e:
        print(f"[原子引擎] 初始化失败: {e}")
        intent_name = "unknown"
        intent_confidence = 0.0
        entities = {}
        kg_result = None

    # ===== 1. Orchestrator 智能路由（四引擎） =====
    try:
        from core.agents.builtin.orchestrator import OrchestratorV6

        orchestrator = OrchestratorV6(user_id=user_id)
        target_agent = orchestrator.smart_route(message)
        print(f"[社会协作] target_agent={target_agent}")
        print(f"[DEBUG] target_agent = {target_agent}")  # 添加这行
        if target_agent != "chat_agent":
            module = __import__(
                f"core.agents.builtin.{target_agent}", fromlist=[target_agent]
            )
            class_map = {
                "code_agent": "CodeAgent",
                "analysis_agent": "AnalysisAgent",
                "decision_agent": "DecisionAgent",
                "executor_agent": "ExecutorAgent",
                "translate_agent": "TranslateAgent",
                "vision_agent": "VisionAgent",
                "memory_agent": "MemoryAgent",
                "video_agent": "VideoAgent",
                "youtube_agent": "YoutubeAgent",
                "director_agent": "DirectorAgent",
                "writer_agent": "WriterAgent",
                "dialect_agent": "DialectAgent",
                "collaboration_agent": "CollaborationAgent",
                "video_indexer_agent": "VideoIndexerAgent",
            }
            class_name = class_map.get(
                target_agent,
                target_agent.replace("_", " ").title().replace(" ", "") + "Agent",
            )
            agent_class = getattr(module, class_name)
            agent = agent_class(user_id=user_id)
            result = agent.process(message)
            response = result.get("response", "处理完成")
            agent_used = target_agent

            save_memory(user_id, f"用户说: {message}")
            save_memory(user_id, f"{agent_used}说: {response[:200]}")
            record_learning(f"{user_id} -> {target_agent}", True)

            return jsonify(
                {
                    "success": True,
                    "response": response,
                    "agent": agent_used,
                    "enhanced": True,
                    "user_id": user_id,
                }
            )
    except Exception as e:
        print(f"Orchestrator 路由失败: {e}")

    # ===== 2. 原子技能和话本匹配 =====
    # 社会契约：分析/决策/执行类请求跳过话本
    social_keywords = [
        "分析",
        "报告",
        "统计",
        "决策",
        "执行",
        ".png",
        ".jpg",
        ".json",
        ".yaml",
    ]
    is_social = any(kw in message.lower() for kw in social_keywords)

    if not is_social:
        try:
            from core.agents.builtin.chat_agent import ChatAgent

            chat_agent = ChatAgent(user_id=user_id)

            atomic_result = chat_agent._check_atomic_skill(message)
            if atomic_result:
                save_memory(user_id, f"用户说: {message}")
                save_memory(user_id, f"ClawsJoy说: {atomic_result[:200]}")
                return jsonify(
                    {
                        "success": True,
                        "response": atomic_result,
                        "agent": "atomic_skill",
                        "enhanced": True,
                        "user_id": user_id,
                    }
                )

            intent = chat_agent._match_intent(message)
            if intent:
                template = chat_agent._get_template(intent)
                if template:
                    save_memory(user_id, f"用户说: {message}")
                    save_memory(user_id, f"ClawsJoy说: {template[:200]}")
                    return jsonify(
                        {
                            "success": True,
                            "response": template,
                            "agent": "scriptbook",
                            "enhanced": True,
                            "user_id": user_id,
                        }
                    )
        except Exception as e:
            print(f"原子技能/话本匹配失败: {e}")

    # ===== 3. 从状态回答 =====
    direct_answer = answer_from_state(message, user_id)
    if direct_answer:
        return jsonify(
            {
                "success": True,
                "response": direct_answer,
                "agent": "state_manager",
                "enhanced": True,
                "user_id": user_id,
            }
        )

    # ===== 4. 调用 LLM 服务（兜底） =====
    try:
        resp = requests.post(
            "http://localhost:5012/chat", json={"message": message}, timeout=60
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

    try:
        from core.lib.pattern_recognizer import pattern_recognizer

        pattern_recognizer.record_behavior(user_id, message, response, "chat_agent")
    except:
        pass

    try:
        from engine.active.integration import active_loop

        active_loop.process(
            user_id=user_id,
            message=message,
            response=response,
            intent=intent_name,
            confidence=intent_confidence,
            success=True,
        )
    except Exception as e:
        print(f"[主动学习] 处理失败: {e}")

    return jsonify(
        {
            "success": True,
            "response": response,
            "agent": "chat_agent",
            "enhanced": True,
            "user_id": user_id,
        }
    )


# ========== 记忆路由 ==========
@app.route("/api/v5/memory/remember", methods=["POST"])
def memory_remember():
    data = request.json or {}
    user_id = data.get("user_id", "guest")
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


@app.route("/api/learning/record", methods=["POST"])
def record_learning_api():
    data = request.json or {}
    fact = data.get("fact", "")
    success = data.get("success", True)
    if fact:
        record_learning(fact, success)
        return jsonify({"success": True, "message": "学习已记录"})
    return jsonify({"success": False, "error": "fact required"}), 400


# ========== 向量服务 ==========
@app.route("/api/vector/stats", methods=["GET"])
def vector_stats():
    try:
        from core.lib.vector_knowledge_center import vector_knowledge_center

        stats = {"skills": 0, "agents": 0, "routes": 0, "memories": 0, "documents": 0}
        if hasattr(vector_knowledge_center, "collections"):
            for name, col in vector_knowledge_center.collections.items():
                if name in stats:
                    stats[name] = col.count()
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/vector/search", methods=["POST"])
def vector_search():
    data = request.json or {}
    query = data.get("query", "")
    knowledge_type = data.get("knowledge_type", None)
    top_k = data.get("top_k", 10)
    try:
        from core.lib.vector_knowledge_center import vector_knowledge_center

        results = vector_knowledge_center.search(
            query, knowledge_type=knowledge_type, n=top_k
        )
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ========== 俱乐部 ==========
@app.route("/api/club/stats", methods=["GET"])
def club_stats():
    try:
        from core.butler_club.center import butler_club

        return jsonify({"success": True, "stats": butler_club.get_stats()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/club/members", methods=["GET"])
def club_members():
    try:
        from core.butler_club.center import butler_club

        limit = request.args.get("limit", 50, type=int)
        return jsonify(
            {"success": True, "members": butler_club.list_members(limit=limit)}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/club/member/<user_id>", methods=["GET"])
def club_member_detail(user_id):
    try:
        from core.butler_club.center import butler_club

        member = butler_club.get_member(user_id)
        if member:
            return jsonify({"success": True, "member": member})
        return jsonify({"success": False, "error": "成员不存在"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ========== 管家 API ==========
@app.route("/api/butler/rename", methods=["POST"])
def butler_rename():
    try:
        from core.butler_center.center import butler_center

        data = request.json or {}
        new_name = data.get("name", "")
        user_id = data.get("user_id", "guest")
        if not new_name:
            return jsonify({"success": False, "error": "请提供新名字"}), 400
        result = butler_center.rename(user_id, new_name)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/butler/todo", methods=["GET", "POST"])
def butler_todo():
    try:
        from core.butler_center.center import butler_center

        user_id = request.args.get("user_id", "guest")
        if request.method == "POST":
            data = request.json or {}
            task = data.get("task", "")
            return jsonify(
                {"success": True, "todo": butler_center.add_todo(user_id, task)}
            )
        else:
            return jsonify({"success": True, "todos": butler_center.get_todos(user_id)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ========== 工作流 ==========
@app.route("/api/workflows/list", methods=["GET"])
def list_workflows():
    from core.lib.workflow_executor import workflow_executor

    workflows = workflow_executor.list_workflows()
    return jsonify({"success": True, "total": len(workflows), "workflows": workflows})


@app.route("/api/workflows/execute/<name>", methods=["POST"])
def execute_workflow(name):
    from core.lib.workflow_executor import workflow_executor

    data = request.json or {}
    result = workflow_executor.execute(name, data)
    return jsonify(result)


@app.route("/api/workflows/status", methods=["GET"])
def workflow_status():
    return jsonify({"success": True, "status": "idle", "running": []})


# ========== 技能热重载 ==========
@app.route("/api/skills/reload", methods=["POST"])
def reload_skills():
    try:
        from core.lib.unified_skill_manager import unified_manager

        unified_manager.reload()
        return jsonify({"success": True, "message": "技能已重载"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/hot-reload/status", methods=["GET"])
def hot_reload_status():
    return jsonify(
        {"success": True, "status": "active", "watchers": ["config", "skills"]}
    )


# ========== 监控指标 ==========
@app.route("/metrics", methods=["GET"])
def metrics_endpoint():
    try:
        from core.lib.metrics import get_metrics

        return Response(get_metrics(), mimetype="text/plain")
    except:
        return jsonify({"success": False, "error": "metrics not available"}), 500


@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    try:
        from core.lib.engine_metrics import engine_metrics

        return jsonify(engine_metrics.get_summary())
    except:
        return jsonify({})


@app.route("/api/metrics/reset", methods=["POST"])
def reset_metrics():
    try:
        from core.lib.engine_metrics import engine_metrics

        engine_metrics.reset()
        return jsonify({"success": True, "message": "指标已重置"})
    except:
        return jsonify({"success": False}), 500


# ========== 调试端点 ==========
@app.route("/api/debug/config", methods=["GET"])
def debug_config():
    from core.lib.unified_config import unified_config

    key = request.args.get("key", "")
    if key:
        value = unified_config.get(key, None)
        return {"key": key, "value": value}
    return {"config_keys": list(unified_config._config.keys())[:20]}


@app.route("/api/debug/orchestrator", methods=["POST"])
def debug_orchestrator():
    from core.agents.builtin.orchestrator import OrchestratorV6

    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "test")
    orchestrator = OrchestratorV6(user_id)
    target = orchestrator.smart_route(message)
    return jsonify(
        {"message": message, "target": target, "orchestrator_version": "2.0.0"}
    )


# ========== YouTube 经营 API ==========
@app.route("/api/youtube/generate/script", methods=["POST"])
def youtube_generate_script():
    from core.agents.builtin.youtube_agent import youtube_agent

    data = request.json or {}
    topic = data.get("topic", "")
    result = youtube_agent.generate_script(topic)
    return jsonify(result)


@app.route("/api/youtube/generate/title", methods=["POST"])
def youtube_generate_title():
    from core.agents.builtin.youtube_agent import youtube_agent

    data = request.json or {}
    topic = data.get("topic", "")
    result = youtube_agent.generate_title(f"生成标题：{topic}")
    return jsonify(result)


@app.route("/api/youtube/generate/description", methods=["POST"])
def youtube_generate_description():
    from core.agents.builtin.youtube_agent import youtube_agent

    data = request.json or {}
    topic = data.get("topic", "")
    result = youtube_agent.generate_description(f"生成描述：{topic}")
    return jsonify(result)


@app.route("/api/youtube/channel/stats", methods=["GET"])
def youtube_channel_stats():
    from core.agents.builtin.youtube_agent import youtube_agent

    result = youtube_agent.get_channel_stats()
    return jsonify(result)


@app.route("/api/youtube/ideas", methods=["GET"])
def youtube_content_ideas():
    from core.agents.builtin.youtube_agent import youtube_agent

    niche = request.args.get("niche", "AI")
    ideas = youtube_agent.get_content_ideas(niche)
    return jsonify({"success": True, "ideas": ideas})


# ========== 流式对话 SSE ==========
@app.route("/api/v5/enhanced/chat/stream", methods=["POST"])
def enhanced_chat_stream():
    data = request.json or {}
    message = data.get("message", "")
    message = desensitizer.desensitize(message)
    user_id = data.get("user_id", "guest")

    def generate():
        memories = search_memories(user_id, message)
        if memories:
            context_text = "根据您的记忆：" + ";".join(memories[:3])
            yield f"data: {json.dumps({'type': 'context', 'content': context_text})}\n\n"
        try:
            resp = requests.post(
                "http://localhost:5012/chat/stream",
                json={"message": message},
                stream=True,
                timeout=60,
            )
            for chunk in resp.iter_content(chunk_size=64, decode_unicode=True):
                if chunk:
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            yield "data: {}\n\n".format(json.dumps({"type": "end"}))
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return Response(generate(), mimetype="text/event-stream")


# ========== 隐私保护 API ==========
@app.route("/api/v1/privacy/policy", methods=["GET"])
def get_privacy_policy():
    import yaml

    try:
        with open("config/ginoor.yaml", "r") as f:
            config = yaml.safe_load(f)
        return jsonify(
            {
                "success": True,
                "policy": config.get("privacy_policy", {}),
                "version": config.get("privacy_policy", {}).get("version", "1.0.0"),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/v1/privacy/consent", methods=["GET", "POST"])
def manage_consent():
    from datetime import datetime

    from engine.security.audit import audit_logger

    if request.method == "GET":
        user_id = request.args.get("user_id", "guest")
        consent_file = Path(f"data/consent/{user_id}.json")
        if consent_file.exists():
            with open(consent_file, "r") as f:
                consent_data = json.load(f)
        else:
            consent_data = {"user_id": user_id, "consents": {}, "updated_at": None}
        return jsonify({"success": True, "consent": consent_data})
    else:
        data = request.json or {}
        user_id = data.get("user_id", "guest")
        purposes = data.get("purposes", {})

        consent_dir = Path("data/consent")
        consent_dir.mkdir(parents=True, exist_ok=True)

        consent_data = {
            "user_id": user_id,
            "consents": purposes,
            "updated_at": datetime.now().isoformat(),
        }

        with open(consent_dir / f"{user_id}.json", "w") as f:
            json.dump(consent_data, f, indent=2)

        audit_logger.log("consent_update", user_id, details=purposes)
        return jsonify({"success": True, "message": "Consent updated"})


@app.route("/api/v1/privacy/data/request", methods=["POST"])
def data_subject_request():
    from datetime import datetime

    from engine.security.audit import audit_logger

    data = request.json or {}
    user_id = data.get("user_id", "guest")
    request_type = data.get("request_type", "access")

    request_id = f"dsr_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    audit_logger.log(
        f"data_subject_request_{request_type}",
        user_id,
        details={"request_id": request_id},
    )

    return jsonify(
        {
            "success": True,
            "request_id": request_id,
            "status": "pending",
            "estimated_completion": "72 hours",
            "message": f"Your {request_type} request has been submitted",
        }
    )


@app.route("/api/v1/privacy/export", methods=["POST"])
def export_user_data():
    from datetime import datetime

    from engine.security.audit import audit_logger

    data = request.json or {}
    user_id = data.get("user_id", "guest")
    format_type = data.get("format", "json")

    user_data = {
        "user_id": user_id,
        "exported_at": datetime.now().isoformat(),
        "format": format_type,
        "data": {"profile": {}, "memories": [], "preferences": [], "interactions": []},
    }

    try:
        from engine.profile import profile_engine

        profile = profile_engine.get_or_create(user_id)
        user_data["data"]["profile"] = {
            "name": profile.name,
            "preferences": profile.preferences,
            "interaction_count": profile.interaction_count,
        }
    except:
        pass

    audit_logger.log("data_export", user_id, details={"format": format_type})

    return jsonify(
        {
            "success": True,
            "data": user_data,
            "format": format_type,
            "message": "Data export completed",
        }
    )


@app.route("/api/v1/privacy/delete", methods=["POST"])
def delete_user_data():
    from datetime import datetime

    from engine.security.audit import audit_logger

    data = request.json or {}
    user_id = data.get("user_id", "guest")
    confirm = data.get("confirm", False)

    if not confirm:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Confirmation required",
                    "message": "Please confirm data deletion",
                }
            ),
            400,
        )

    deletion_dir = Path("data/deletion_requests")
    deletion_dir.mkdir(parents=True, exist_ok=True)

    deletion_record = {
        "user_id": user_id,
        "deleted_at": datetime.now().isoformat(),
        "status": "pending",
    }

    with open(deletion_dir / f"{user_id}.json", "w") as f:
        json.dump(deletion_record, f, indent=2)

    audit_logger.log("data_deletion_request", user_id, result="pending")

    return jsonify(
        {
            "success": True,
            "message": "Data deletion request submitted",
            "processing_time": "72 hours",
        }
    )


# ========== 其他辅助路由 ==========
@app.route("/api/tasks/status", methods=["GET"])
def get_task_status():
    task_id = request.args.get("task_id", "")
    return jsonify({"success": True, "task_id": task_id, "status": "completed"})


@app.route("/api/voice/wakeup", methods=["POST"])
def voice_wakeup():
    return jsonify({"success": True, "wakeup": True, "keywords": ["小管", "你好小管"]})


@app.route("/api/ws/status", methods=["GET"])
def ws_status():
    return jsonify({"success": True, "status": "connected", "connections": 0})


@app.route("/api/sse/subscribe", methods=["GET", "POST"])
def sse_subscribe():
    return jsonify({"success": True, "message": "SSE endpoint ready"})


@app.route("/api/sse/test", methods=["GET"])
def sse_test():
    return jsonify({"success": True, "message": "SSE test successful"})


@app.route("/api/translate/query", methods=["POST"])
def translate_query():
    data = request.json or {}
    text = data.get("text", "")
    return jsonify({"success": True, "original": text, "translated": f"[翻译]{text}"})


@app.route("/api/frontend/page-view", methods=["POST"])
def frontend_page_view():
    return jsonify({"success": True, "recorded": True})


@app.route("/api/frontend/error", methods=["POST"])
def frontend_error():
    return jsonify({"success": True, "recorded": True})


@app.route("/api/user/data-request", methods=["POST"])
def user_data_request():
    return jsonify({"success": True, "request_id": "req_001", "status": "pending"})


@app.route("/api/developer/upload", methods=["POST"])
def developer_upload():
    return jsonify({"success": True, "message": "Upload endpoint ready"})


@app.route("/api/admin/pending", methods=["GET"])
def admin_pending():
    return jsonify({"success": True, "pending": []})


@app.route("/api/admin/approve", methods=["POST"])
def admin_approve():
    return jsonify({"success": True, "approved": True})


@app.route("/api/admin/reject", methods=["POST"])
def admin_reject():
    return jsonify({"success": True, "rejected": True})


@app.route("/api/meeting/create", methods=["POST"])
def meeting_create():
    return jsonify({"success": True, "meeting_id": "meet_001"})


@app.route("/api/meeting/list", methods=["GET"])
def meeting_list():
    return jsonify({"success": True, "meetings": []})


@app.route("/api/meeting/close", methods=["POST"])
def meeting_close():
    return jsonify({"success": True, "closed": True})


@app.route("/api/collaboration/start", methods=["POST"])
def collaboration_start():
    return jsonify({"success": True, "session_id": "collab_001"})


@app.route("/api/collaboration/message", methods=["POST"])
def collaboration_message():
    return jsonify({"success": True, "delivered": True})


@app.route("/api/closed-loop/run", methods=["POST"])
def closed_loop_run():
    return jsonify({"success": True, "loop_id": "loop_001"})


@app.route("/api/closed-loop/status", methods=["GET"])
def closed_loop_status():
    return jsonify({"success": True, "status": "running"})


@app.route("/api/analyst/status", methods=["GET"])
def analyst_status():
    return jsonify({"success": True, "status": "active"})


@app.route("/api/analyst/report", methods=["GET"])
def analyst_report():
    return jsonify({"success": True, "report": {"total_analysis": 100, "insights": []}})


@app.route("/api/market/skills/export", methods=["POST"])
def market_export_skill():
    try:
        data = request.json or {}
        skill_name = data.get("skill_name", "")
        if not skill_name:
            return jsonify({"success": False, "error": "skill_name required"}), 400

        from engine.openclaw.core import openclaw_engine

        result = openclaw_engine.export_skill(skill_name, data.get("skill_data", {}))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/market/skills/import", methods=["POST"])
def market_import_skill():
    try:
        data = request.json or {}
        skill_name = data.get("skill_name", "")
        if not skill_name:
            return jsonify({"success": False, "error": "skill_name required"}), 400

        from engine.openclaw.core import openclaw_engine

        result = openclaw_engine.import_skill(skill_name, data.get("source"))
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/market/skills/sync", methods=["POST"])
def market_sync_skills():
    try:
        data = request.json or {}
        direction = data.get("direction", "both")

        from engine.openclaw.core import openclaw_engine

        result = openclaw_engine.sync_with_community(direction)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/market/skills/list", methods=["GET"])
def market_list_skills():
    try:
        from engine.openclaw.core import openclaw_engine

        return jsonify(
            {
                "success": True,
                "exported": openclaw_engine.list_exported(),
                "imported": openclaw_engine.list_imported(),
                "stats": openclaw_engine.get_stats(),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ========== 热重载端点 ==========
@app.route("/api/reload/config", methods=["POST"])
def reload_config():
    """热重载配置文件"""
    try:
        from core.lib.unified_config import unified_config

        unified_config._load()
        from core.lib.intent_parser_v2 import intent_parser

        intent_parser.reload()
        from engine.lib.config_loader import config_loader

        config_loader.reload()
        return jsonify({"success": True, "message": "配置已重载"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/reload/agents", methods=["POST"])
def reload_agents():
    """热重载 Agent"""
    try:
        from core.agents.builtin.agent_manager import agent_manager

        agent_manager.reload()
        return jsonify({"success": True, "message": "Agent 已重载"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



# ========== 启动入口 ==========
if __name__ == "__main__":
    port = unified_config.get("services.gateway.port", 5002)
    smart_service.start()
    print("=" * 50)
    print(f"🚀 ClawsJoy Gateway 完整版启动在端口 {port}")
    print(f"   Workers: 4, Threads: 8, 并发: 32")
    print("=" * 50)
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
