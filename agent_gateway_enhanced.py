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
    from flask import send_from_directory
    return send_from_directory('templates', 'codex.html')

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
        self._lock = __import__('threading').Lock()  # 线程锁

    def get(self, key):
        with self._lock:
            if key in self.cache:
                data, timestamp = self.cache[key]
                if datetime.now().timestamp() - timestamp < self.ttl:
                    return data
                del self.cache[key]
        return None

    def set(self, key, value):
        with self._lock:
            self.cache[key] = (value, datetime.now().timestamp())

    def clear(self):
        with self._lock:
            self.cache.clear()

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
# 替换记忆函数
def _get_memory_agent(user_id):
    """获取 MemoryAgent 实例"""
    try:
        from agents.memory_agent.agent_v4 import MemoryAgentV4
        return MemoryAgentV4(user_id)
    except Exception as e:
        logger.warning(f"MemoryAgent 不可用: {e}")
        return None

def load_memories(user_id):
    """加载记忆 - 优先使用 MemoryAgent"""
    agent = _get_memory_agent(user_id)
    if agent:
        try:
            # 调用 MemoryAgent 获取记忆
            result = agent.recall_forever("all_memories")
            if result:
                return result if isinstance(result, list) else [result]
        except Exception as e:
            logger.warning(f"MemoryAgent 加载失败: {e}")
    
    # 降级到本地文件存储
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            all_memories = json.load(f)
            return all_memories.get(user_id, [])
    return []

# 修改 save_memory 函数，调用 MemoryAgent
def save_memory(user_id, fact):
    try:
        from agents.memory_agent.agent_v4 import MemoryAgentV4
        agent = MemoryAgentV4(user_id)
        agent.remember_forever("fact", fact)
        return
    except Exception as e:
        logger.warning(f"MemoryAgent 不可用: {e}")   
    # 降级到本地文件存储
    memories = []
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            all_memories = json.load(f)
            memories = all_memories.get(user_id, [])
    
    memories.append({"fact": fact, "timestamp": datetime.now().isoformat()})
    all_memories = {}
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            all_memories = json.load(f)
    all_memories[user_id] = memories[-100:]
    with open(MEMORY_FILE, "w") as f:
        json.dump(all_memories, f, indent=2)

def search_memories(user_id, query):
    """搜索记忆 - 优先使用 MemoryAgent"""
    agent = _get_memory_agent(user_id)
    if agent:
        try:
            result = agent.process(f"搜索记忆: {query}")
            if result and result.get("response"):
                return [result.get("response")]
        except Exception as e:
            logger.warning(f"MemoryAgent 搜索失败: {e}")
    
    # 降级到本地搜索
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


# ========== 项目级用户状态管理 ==========
import json
from pathlib import Path
from typing import Dict, Any, Optional

class ProjectUserState:
    """项目级用户状态 - 存储在项目 .clawsjoy/ 目录下"""
    
    def __init__(self, project_id: str = None, user_id: str = "default"):
        self.project_id = project_id
        self.user_id = user_id
        self._state: Dict[str, Any] = {}
        self._load()
    
    def _get_state_path(self) -> Path:
        """获取状态文件路径"""
        if self.project_id:
            try:
                from core.lib.code_repo import get_code_repo
                repo = get_code_repo(self.user_id)
                project = repo.get_project(self.project_id)
                if project:
                    project_path = Path(project["path"])
                    state_dir = project_path / ".clawsjoy"
                    state_dir.mkdir(exist_ok=True)
                    return state_dir / "user_state.json"
            except Exception as e:
                print(f"获取项目路径失败: {e}")
        
        # 降级到全局目录
        state_dir = Path(f"data/user_states/{self.user_id}")
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir / "state.json"
    
    def _load(self):
        path = self._get_state_path()
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self._state = json.load(f)
            except:
                self._state = {}
        else:
            self._state = {}
    
    def _save(self):
        path = self._get_state_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self._state, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default=None):
        return self._state.get(key, default)
    
    def set(self, key: str, value):
        self._state[key] = value
        self._save()
    
    def get_all(self) -> Dict:
        return self._state.copy()


# 全局状态缓存
_USER_STATE_CACHE: Dict[str, ProjectUserState] = {}


def _get_state_key(project_id: str = None, user_id: str = "default") -> str:
    """生成状态缓存键"""
    return f"{project_id or 'global'}_{user_id}"


def get_user_state(project_id: str = None, user_id: str = "default") -> Dict:
    """获取用户状态（支持项目级）"""
    key = _get_state_key(project_id, user_id)
    if key not in _USER_STATE_CACHE:
        _USER_STATE_CACHE[key] = ProjectUserState(project_id, user_id)
    return _USER_STATE_CACHE[key].get_all()


def set_user_state(project_id: str, user_id: str, key: str, value):
    """设置用户状态"""
    key_id = _get_state_key(project_id, user_id)
    if key_id not in _USER_STATE_CACHE:
        _USER_STATE_CACHE[key_id] = ProjectUserState(project_id, user_id)
    _USER_STATE_CACHE[key_id].set(key, value)


def extract_user_info(message: str, user_id: str, project_id: str = None) -> bool:
    """提取用户信息（支持项目级）"""
    from core.lib.security_hooks import SecurityHooks
    
    # 安全检查
    ok, cleaned_msg = SecurityHooks.sanitize_input(message)
    if not ok:
        logger.warning(f"输入清洗失败")
        return False
    
    ok, error_msg = SecurityHooks.check_dangerous_patterns(cleaned_msg)
    if not ok:
        logger.warning(f"危险模式: {error_msg}")
        return False
    
    # 提取名字
    name_match = re.search(r"我叫([\u4e00-\u9fa5]{2,4})", cleaned_msg)
    if name_match:
        name = name_match.group(1)
        # 存储到项目级状态
        set_user_state(project_id, user_id, "user_name", name)
        save_memory(user_id, f"用户名字: {name}")
        save_memory(user_id, f"用户说: 我叫{name}")
        return True
    
    return False


def answer_from_state(message: str, user_id: str, project_id: str = None) -> Optional[str]:
    """从状态中回答用户问题（支持项目级）"""
    if "我叫什么名字" in message or "我的名字" in message:
        # 优先从项目级状态获取
        state = get_user_state(project_id, user_id)
        name = state.get("user_name")
        
        if name:
            return f"您叫{name}呀，我记着呢！"
        
        # 降级到记忆系统
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
                    name = fact[start + 2: start + 6].strip("，。！？")
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

        # 业务指标值（安全获取）
        try:
            requests_total = request_count._value.get() if hasattr(request_count, '_value') else 0
            sessions_total = active_sessions._value.get() if hasattr(active_sessions, '_value') else 0
        except Exception:
            requests_total = 0
            sessions_total = 0

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
    """动态获取 Agent 列表 - 从 wisdom_factory 读取"""
    try:
        from core.agents.wisdom.wisdom_factory import wisdom_factory
        
        agents_list = []
        # 获取所有已注册的 V4 Agent
        v4_agent_names = [
            "analysis_agent", "audio_agent", "butler_agent", "calculator_agent",
            "chat_agent", "code_agent", "collaboration_agent", "decision_agent",
            "dialect_agent", "file_agent", "memory_agent", "orchestrator",
            "proactive_agent", "three_d_agent", "translate_agent", "video_agent",
            "video_indexer_agent", "vision_agent", "writer_agent", "youtube_agent"
        ]
        
        for name in v4_agent_names:
            agents_list.append({
                "name": name,
                "status": "active",
                "version": "4.0.0"
            })
        
        agents_list.sort(key=lambda x: x["name"])
        
        return jsonify({"success": True, "total": len(agents_list), "agents": agents_list})
    except Exception as e:
        # 降级到备用列表
        fallback_agents = [
            {"name": "chat_agent", "status": "active", "version": "4.0.0"},
            {"name": "code_agent", "status": "active", "version": "4.0.0"},
            {"name": "analysis_agent", "status": "active", "version": "4.0.0"},
            {"name": "orchestrator", "status": "active", "version": "4.0.0"},
        ]
        return jsonify({"success": True, "total": len(fallback_agents), "agents": fallback_agents})      

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

@app.route("/api/v5/enhanced/chat", methods=["POST"])
def enhanced_chat():
    """
    [DEPRECATED] 增强对话接口 - 请使用 /api/v5/wisdom/chat 替代
    
    此接口将在后续版本中移除，请尽快迁移到新接口。
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 记录废弃警告
    logger.warning("⚠️ 使用了废弃接口 /api/v5/enhanced/chat，调用方: %s", request.remote_addr)
    
    # 直接转发到 wisdom_chat 接口
    # 保持原有数据格式，避免破坏兼容性
    data = request.json or {}
    
    # 调用 wisdom_chat 的底层逻辑
    try:
        # 重新构建请求到 wisdom_chat 的入口
        from flask import Request
        with app.test_request_context():
            # 创建新的请求上下文
            request._get_current_object()
        
        # 直接调用 wisdom_chat 函数
        response = wisdom_chat()
        
        # 添加废弃标记
        if hasattr(response, 'headers'):
            response.headers['X-API-Deprecated'] = 'true'
            response.headers['X-API-Migration'] = '/api/v5/wisdom/chat'
            response.headers['X-API-Sunset-Date'] = '2026-09-01'
        
        return response
    except Exception as e:
        logger.error(f"转发到 wisdom_chat 失败: {e}")
        # 降级到原有逻辑
        return _legacy_enhanced_chat()

def _legacy_enhanced_chat():
    """原有 enhanced_chat 逻辑，作为降级备份"""
    data = request.json or {}
    user_id = data.get("user_id", "guest")
    message = data.get("message", "")
    
    # 原有降级逻辑
    from core.lib.chat_engine import chat_engine
    result = chat_engine.execute(message, user_id)
    return jsonify(result)


# ========== 记忆路由 ==========
@app.route("/api/v5/memory/remember", methods=["POST"])
# 未来可考虑统一使用 MemoryAgent
def memory_remember():
    data = request.json or {}
    user_id = data.get("user_id", "guest")
    fact = data.get("fact", "")
    
    try:
        from agents.memory_agent.agent_v4 import MemoryAgentV4
        agent = MemoryAgentV4(user_id)
        result = agent.process(f"记住 {fact}")
        if result.get("success"):
            return jsonify({"success": True, "message": "记忆已存储"})
    except:
        pass
    
    # 降级到原有逻辑
    save_memory(user_id, fact)
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
    logger.warning(f"废弃接口被调用: /api/agent/{agent_name}/message，请迁移到 /api/v5/wisdom/chat")
    # 内部转发到 wisdom_factory
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
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    email = data.get("email", "")

    if not username or not password:
        return jsonify({"success": False, "error": "用户名和密码不能为空"}), 400

    result = auth_manager.register(username, password, role="user")

    if result.get("success"):
        user_id = result.get("user_id")
        
        # 创建用户目录（统一处理，避免重复）
        _create_user_directories(username, user_id, email)
        
        logger.info(f"用户注册成功: {username} ({user_id})")
        return jsonify(result)
    else:
        return jsonify(result), 400


def _create_user_directories(username, user_id, email):
    """创建用户目录结构（统一函数）"""
    import json
    from pathlib import Path
    from datetime import datetime
    
    user_dir = Path(f"data/users/{username}")
    if user_dir.exists():
        return
    
    user_dir.mkdir(parents=True)
    
    # 创建所有必要子目录
    subdirs = [
        "encrypted", "communications/inbox", "communications/outbox",
        "communications/archive", "youtube_data", "scripts", "videos",
        "images", "logs", "workspace"
    ]
    for subdir in subdirs:
        (user_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    # 创建 profile
    profile = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "role": "user",
        "created_at": datetime.now().isoformat(),
        "workspace": str(user_dir / "workspace")
    }
    with open(user_dir / "profile.json", "w") as f:
        json.dump(profile, f, indent=2)


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


# ========== 引擎管理 API ==========
@app.route("/api/v5/admin/engine/chat/status", methods=["GET"])
@require_auth
def get_chat_engine_status():
    """获取对话引擎状态"""

    return jsonify(chat_engine.get_status())


@app.route("/api/v5/admin/engine/chat/enable", methods=["POST"])
@require_auth
def enable_chat_engine():
    """启用对话引擎（需要管理员权限）"""
    # 检查用户角色
    if not is_admin(g.user_id):
        return jsonify({"success": False, "error": "需要管理员权限"}), 403
    
    chat_engine.enabled = True
    return jsonify({"success": True, "message": "对话引擎已启用", "status": chat_engine.get_status()})

@app.route("/api/v5/admin/engine/chat/disable", methods=["POST"])
@require_auth
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
@require_auth
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
    """流式对话接口 - 使用智慧 Agent 流式输出"""
    from flask import Response, stream_with_context
    import json

    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")
    agent_name = data.get("agent")

    def generate():
        try:
            # 使用 wisdom_factory 获取 Agent
            wisdom_agent = wisdom_factory.get_wisdom_agent(agent_name, user_id)
            if wisdom_agent:
                result = wisdom_agent.process(message)
                response_text = result.get("response", "")
                # 分块输出
                chunk_size = 50
                for i in range(0, len(response_text), chunk_size):
                    chunk = response_text[i:i+chunk_size]
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            else:
                yield f"data: {json.dumps({'error': f'Agent {agent_name} 不可用'})}\n\n"
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
    MAX_FEEDBACK = 1000  # 最大存储数量    
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
    # ========== 优化：限制存储数量 ==========
    for cat in ["success", "failure"]:
        if len(all_feedback[cat]) > MAX_FEEDBACK:
            all_feedback[cat] = all_feedback[cat][-MAX_FEEDBACK:]
    # ====================================
    
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
    agent_name = data.get("agent")
    
    # 验证必要字段
    if not message:
        return jsonify({"success": False, "response": "消息不能为空"}), 400
    
    # ========== 1. 代码分析检测（静态分析，不调用 Agent）==========
    if "分析" in message or "审核" in message or "review" in message.lower() or "深度审查" in message or "深度分析" in message:
        import re
        code_match = re.search(r'```(?:python)?\n(.*?)```', message, re.DOTALL)
        if code_match:
            code_to_analyze = code_match.group(1)
            try:
                from agents.code_agent.agent_v4 import CodeAgentV4 as CodeAgentV4
                ca = CodeAgentV4(user_id)

                # 深度审查使用 deep_review 方法
                if "深度审查" in message or "深度分析" in message:
                    result = ca.deep_review(code_to_analyze, file_path="inline")
                    output = ca._format_review_result(result)
                else:
                    analysis = ca.analyze_code(code_to_analyze, file_path="inline")
                    if analysis.get("success"):
                        # 格式化输出
                        output = f"""## 📊 代码分析报告

### 📈 代码概览
{analysis['summary']}

### 🔧 代码结构
- 总行数: {analysis['metrics']['total_lines']}
- 代码行数: {analysis['metrics']['code_lines']}
- 注释行数: {analysis['metrics']['comment_lines']}
- 函数数量: {analysis['metrics']['functions_count']}
- 类数量: {analysis['metrics']['classes_count']}
- 导入数量: {analysis['metrics']['imports_count']}

### 📦 函数列表
"""
                    for f in analysis.get('functions', []):
                        output += f"- `{f['name']}` (第{f['line']}行)\n"

                    if analysis.get('classes'):
                        output += f"\n### 📦 类列表\n"
                        for c in analysis['classes']:
                            output += f"- `{c['name']}` (第{c['line']}行)\n"

                    if analysis.get('issues'):
                        output += f"\n### ⚠ 问题清单\n\n"
                        output += "| 行号 | 类型 | 严重程度 | 问题描述 |\n"
                        output += "|------|------|----------|----------|\n"
                        for issue in analysis['issues']:
                            output += f"| {issue['line']} | {issue['type']} | {issue['severity']} | {issue['description']} |\n"

                        output += f"\n### 💡 修复建议\n\n"
                        for issue in analysis['issues']:
                            output += f"**L{issue['line']}**: {issue['suggestion']}\n"
                            if issue.get('code_example'):
                                output += f"```python\n{issue['code_example']}\n```\n\n"

                    if analysis.get('suggestions'):
                        output += f"\n### 📝 改进建议\n"
                        for s in analysis['suggestions']:
                            output += f"- {s}\n"

                    output += f"\n---\n💡 **提示**: 用户可以根据以上建议在编辑器中手动修改代码。"
                    return jsonify({"success": True, "response": output, "output_content": output})
            except Exception as e:
                print(f"静态分析失败: {e}")
                # 失败时继续走 Agent 流程
    # ========== 2. 文件内容读取（用于审核按钮）==========
    project_id = data.get("project_id")
    file_path = data.get("file_path")

    if project_id and file_path:
        try:
            file_context, file_info = extract_file_content(project_id, file_path, user_id)
            if file_context:
                message = message + file_context
                print(f"✅ {file_info}")
        except Exception as e:
            print(f"⚠ 读取文件失败: {e}")

    # ========== 3. 消息长度限制 ==========
    if len(message) > 5000:
        return jsonify({"success": False, "response": "消息过长，请控制在5000字符以内"}), 400

    # ========== 4. 智能 Agent 推荐 ==========
    # 如果没有指定 agent，使用 LLM 推荐
    if not agent_name:
        try:
            from core.lib.agent_capability_loader import agent_capability_loader
            
            # 生成推荐提示词
            prompt = agent_capability_loader.get_recommendation_prompt(message)
            print(f"[Wisdom] 请求 LLM 推荐 Agent: {message[:50]}...")
            
            # 调用 LLM 推荐
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:3b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 20}
                },
                timeout=30
            )
            
            if resp.status_code == 200:
                recommended = resp.json().get("response", "").strip()
                print(f"[Wisdom] LLM 原始响应: {recommended}")
                # 清理推荐结果
                recommended = recommended.replace('推荐:', '').replace('Agent:', '').strip()
                print(f"[Wisdom] 清理后: {recommended}")
                # 验证推荐的 Agent 是否存在
                test_agent = wisdom_factory.get_wisdom_agent(recommended, user_id)
                if test_agent:
                    agent_name = recommended
                    print(f"[Wisdom] LLM 推荐 Agent: {agent_name}")
                else:
                    print(f"[Wisdom] LLM 推荐了无效 Agent: {recommended}，使用 orchestrator")
                    agent_name = "orchestrator"
            else:
                print(f"[Wisdom] LLM 推荐失败，使用 orchestrator")
                agent_name = "orchestrator"
        except Exception as e:
            print(f"[Wisdom] Agent 推荐异常: {e}，使用 orchestrator")
            agent_name = "orchestrator"
    
    # 获取 Agent
    if agent_name:
        wisdom_agent = wisdom_factory.get_wisdom_agent(agent_name, user_id)
    else:
        wisdom_agent = wisdom_factory.get_wisdom_agent("orchestrator", user_id)

    if not wisdom_agent:
        return jsonify({"success": False, "response": f"Agent {agent_name} 不可用"}), 404

    # ========== 5. 检测输入类型并处理 ==========
    if "action" in data or "raw_input" in data:
        # 标准化 JSON 输入
        result = wisdom_agent.handle_json(data)
        return jsonify(result)
    else:
        # 自然语言输入
        result = wisdom_agent.process(message)

        # ========== 6. 格式化请求检测（工具调用）==========
        response_text = result.get("response", "") or result.get("output_content", "")

        # 检测是否是格式化请求
        if "格式化" in message:
            import re
            code_match = re.search(r'```(?:python)?\n(.*?)```', message, re.DOTALL)
            if code_match:
                code_to_format = code_match.group(1)
                result["tool_call"] = {
                    "type": "format_request",
                    "tool": "format_python",
                    "args": {"code": code_to_format},
                    "message": f"🔧 检测到代码格式化请求，是否执行格式化？\n\n原代码：\n```python\n{code_to_format[:200]}\n```",
                    "requires_confirmation": True
                }
                result["response"] = response_text + "\n\n🔧 请回复「确认格式化」来执行格式化。"

        return jsonify(result)

@app.route("/api/v5/execute_tool", methods=["POST"])
def execute_tool_api():
    """执行工具调用（需要用户确认后调用）"""
    data = request.json or {}
    user_id = data.get("user_id", "guest")
    tool_name = data.get("tool")
    tool_args = data.get("args", {})

    result = execute_tool(tool_name, tool_args, user_id)
    return jsonify(result)


# ========== 工具调用支持 ==========
def execute_tool(tool_name: str, tool_args: dict, user_id: str) -> dict:
    """执行工具调用"""

    if tool_name == "format_python":
        from agents.code_agent.agent_v4 import CodeAgentV4 as CodeAgentV4
        agent = CodeAgentV4(user_id)
        code = tool_args.get("code", "")
        return agent.format_code_with_autopep8(code)

    elif tool_name == "format_with_black":
        from agents.code_agent.agent_v4 import CodeAgentV4 as CodeAgentV4
        agent = CodeAgentV4(user_id)
        code = tool_args.get("code", "")
        return agent.format_code_with_black(code)

    elif tool_name == "read_file":
        from core.lib.code_repo import get_code_repo
        repo = get_code_repo(user_id)
        project_id = tool_args.get("project_id")
        file_path = tool_args.get("file_path")
        content = repo.get_file_content(project_id, file_path)
        return {"success": True, "content": content}

    elif tool_name == "write_file":
        from core.lib.code_repo import get_code_repo
        repo = get_code_repo(user_id)
        project_id = tool_args.get("project_id")
        file_path = tool_args.get("file_path")
        content = tool_args.get("content")
        # 实现写入逻辑
        return {"success": True, "message": "文件已保存"}

    else:
        return {"success": False, "error": f"未知工具: {tool_name}"}

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
    agent_name = data.get("agent")
    
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
    agent_name = data.get("agent")
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
    agent_name = data.get("agent")
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


# ========== 文件操作 API ==========

@app.route("/api/v5/project/list", methods=["GET"])
def project_list():
    """获取项目列表"""
    user_id = request.args.get("user_id", "codex_user")

    from core.lib.code_repo import get_code_repo
    repo = get_code_repo(user_id)

     # 使用 repo 提供的方法
    projects = repo.list_projects()
    return jsonify({"success": True, "projects": projects})


@app.route("/api/v5/project/add", methods=["POST"])
def project_add():
    """添加项目"""
    data = request.json or {}
    user_id = data.get("user_id", "codex_user")
    project_path = data.get("path", "")

    if not project_path:
        return jsonify({"success": False, "error": "请提供项目路径"}), 400

    path = Path(project_path).expanduser().resolve()
    if not path.exists():
        return jsonify({"success": False, "error": f"路径不存在: {project_path}"}), 404

    # 调用 CodeAgent 添加项目
    from core.lib.code_repo import get_code_repo
    repo = get_code_repo(user_id)
    result = repo.add_project(str(path))

    return jsonify(result)


@app.route("/api/v5/project/<project_id>/files", methods=["GET"])
def project_files(project_id):
    """获取项目文件列表"""
    user_id = request.args.get("user_id", "codex_user")

    from core.lib.code_repo import get_code_repo
    repo = get_code_repo(user_id)

    project = repo.get_project(project_id)
    if not project:
        return jsonify({"success": False, "error": "项目不存在"}), 404

    files = repo.get_files(project_id)

    return jsonify({"success": True, "files": files, "project": project})
@app.route("/api/v5/project/<project_id>/file", methods=["GET"])
def project_file_read(project_id):
    """读取文件内容"""
    user_id = request.args.get("user_id", "codex_user")
    file_path = request.args.get("path", "")

    if not file_path:
        return jsonify({"success": False, "error": "请提供文件路径"}), 400

    from core.lib.code_repo import get_code_repo
    repo = get_code_repo(user_id)

    content = repo.get_file_content(project_id, file_path)
    if content is None:
        return jsonify({"success": False, "error": "文件读取失败"}), 404

    return jsonify({"success": True, "content": content, "path": file_path})


@app.route("/api/v5/project/<project_id>/file", methods=["POST"])
def project_file_save(project_id):
    """保存文件内容"""
    data = request.json or {}
    user_id = data.get("user_id", "codex_user")
    file_path = data.get("path", "")
    content = data.get("content", "")

    if not file_path:
        return jsonify({"success": False, "error": "请提供文件路径"}), 400

    from core.lib.code_repo import get_code_repo
    repo = get_code_repo(user_id)

    project = repo.get_project(project_id)
    if not project:
        return jsonify({"success": False, "error": "项目不存在"}), 404

    full_path = Path(project["path"]) / file_path
    try:
        full_path.write_text(content, encoding='utf-8')
        return jsonify({"success": True, "message": f"已保存: {file_path}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/v5/project/search", methods=["POST"])
def project_search():
    """搜索代码"""
    data = request.json or {}
    user_id = data.get("user_id", "codex_user")
    query = data.get("query", "")
    project_id = data.get("project_id")

    from core.lib.code_repo import get_code_repo
    repo = get_code_repo(user_id)

    results = repo.search_code(query, project_id)
    return jsonify({"success": True, "results": results})



# ========== code弹板路由 ==========
@app.route("/code_agent_panel.html")
def code_agent_panel():
    from flask import send_from_directory
    return send_from_directory("templates", "code_agent_panel.html")


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


