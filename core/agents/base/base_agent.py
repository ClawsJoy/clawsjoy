#!/usr/bin/env python3
"""Base Agent - Base Agent 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""Base Agent - 所有 Agent 的基类

设计原则：
1. 用户隔离 - 每个用户数据独立存储
2. 配置驱动 - 行为由 YAML 配置，支持多级覆盖
3. 记忆内置 - 所有 Agent 默认有 L0-L2 记忆能力
4. 生命周期 - 提供启动/停止钩子
5. 跨区学习 - 内置知识分享能力
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from datetime import datetime
import json
import yaml
import uuid


class BaseAgent:
    """Agent 基类 - 所有 Agent 应继承此类"""

    # 版本号
    VERSION = "2.0.0"

    # Agent 元信息（子类覆盖）
    name: str = "base_agent"
    description: str = "基础 Agent"
    type: str = "core"  # core, custom, skill

    def __init__(self, user_id: str = "default", agent_id: Optional[str] = None):
        """
        初始化 Agent

        Args:
            user_id: 用户标识（用于数据隔离）
            agent_id: Agent 实例标识（可选，自动生成）
        """
        self.user_id = user_id
        self.agent_id = agent_id or f"{self.name}_{uuid.uuid4().hex[:8]}"

        # 初始化时间
        self.created_at = datetime.now()
        self.last_active = self.created_at

        # ========== 目录结构 ==========
        # 用户数据目录（隔离）
        self.user_dir = Path(f"{get_data_root()}/users/{user_id}")

        # Agent 工作目录
        self.work_dir = self.user_dir / "agents" / self.name
        self.work_dir.mkdir(parents=True, exist_ok=True)

        # 记忆目录
        self.memory_dir = self.work_dir / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # 配置目录
        self.config_dir = self.work_dir / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # ========== 记忆系统 ==========
        self._memory: Dict = {}
        self._load_memory()

        # ========== 配置系统 ==========
        self._config: Dict = {}
        self._load_config()

        # ========== 统计信息 ==========
        self._update_stats()
        # ========== 传承系统 ==========
        self.inheritance = None
        # self._init_inheritance()  # 配置驱动，暂不启用


        # 调用生命周期钩子
        self.on_init()

        self.log(f"Agent 初始化完成 v{self.VERSION}")
    
    # ==================== 记忆系统 ====================
    
    def _load_memory(self) -> None:
        """加载记忆"""
        memory_file = self.memory_dir / "memory.json"
        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    self._memory = json.load(f)
            except Exception as e:
                self.log(f"加载记忆失败: {e}", "WARN")

        # 初始化默认结构
        if "preferences" not in self._memory:
            self._memory["preferences"] = {}
        if "history" not in self._memory:
            self._memory["history"] = []
        if "stats" not in self._memory:
            self._memory["stats"] = {
                "total_interactions": 0,
                "created_at": datetime.now().isoformat()
            }
        if "shared" not in self._memory:
            self._memory["shared"] = {}
    
    
    @property
    def memory(self) -> Any:
        """兼容旧代码：返回 _memory"""
        return self._memory
    
    @memory.setter
    def memory(self, value) -> Any:
        """兼容旧代码：设置 _memory"""
        self._memory = value

    def _save_memory(self) -> None:
        """保存记忆"""
        memory_file = self.memory_dir / "memory.json"
        try:
            with open(memory_file, 'w') as f:
                json.dump(self._memory, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            self.log(f"保存记忆失败: {e}", "ERROR")
    
    def remember(self, key: str, value: Any, shared: bool = False) -> bool:
        """
        记住信息

        Args:
            key: 信息键名
            value: 信息值
            shared: 是否共享给其他 Agent
        """
        target = "shared" if shared else "preferences"
        if target not in self._memory:
            self._memory[target] = {}
        self._memory[target][key] = value
        self._save_memory()
        self.log(f"已记住: {key} = {str(value)[:50]}")
    
    def recall(self, key: str) -> Optional[Any]:
        """
        回忆信息（优先私有，再共享）

        Args:
            key: 信息键名

        Returns:
            存储的值，不存在则返回 None
        """
        # 先查私有偏好
        if key in self._memory.get("preferences", {}):
            return self._memory["preferences"][key]
        # 再查共享记忆
        if key in self._memory.get("shared", {}):
            return self._memory["shared"][key]
        return None
    
    def forget(self, key: str) -> Any:
        """忘记信息"""
        if key in self._memory.get("preferences", {}):
            del self._memory["preferences"][key]
        if key in self._memory.get("shared", {}):
            del self._memory["shared"][key]
        self._save_memory()
    
    def record_interaction(self, user_input: str, response: str) -> Any:
        """记录交互历史"""
        if "history" not in self._memory:
            self._memory["history"] = []

        self._memory["history"].append({
            "user": user_input,
            "agent": response,
            "timestamp": datetime.now().isoformat()
        })

        # 限制历史长度（默认保留 100 条）
        max_history = self._config.get("memory", {}).get("max_history", 100)
        if len(self._memory["history"]) > max_history:
            self._memory["history"] = self._memory["history"][-max_history:]

        self._save_memory()
    
    # ==================== 配置系统 ====================
    
    def _load_config(self) -> None:
        """加载配置 - 统一从工作区加载"""
        config = {}

        # 1. 工作区配置（优先）
        workspace_config = Path(f"agents/{self.name}/config.yaml")
        if workspace_config.exists():
            try:
                with open(workspace_config, 'r') as f:
                    ws_config = yaml.safe_load(f)
                    if ws_config:
                        config.update(ws_config)
                        self.log(f"已加载工作区配置: {workspace_config}")
            except Exception as e:
                self.log(f"加载工作区配置失败: {e}", "WARN")

        # 2. 用户配置（覆盖）
        user_config = self.config_dir / "config.yaml"
        if user_config.exists():
            try:
                with open(user_config, 'r') as f:
                    user_config_data = yaml.safe_load(f)
                    if user_config_data:
                        self._deep_merge(config, user_config_data)
                        self.log(f"已加载用户配置: {user_config}")
            except Exception as e:
                self.log(f"加载用户配置失败: {e}", "WARN")

        # 3. 兼容旧路径：系统级配置（回退）
        if not config:
            system_config = Path(f"{get_data_root()}/system/agents/{self.name}/config.yaml")
            if system_config.exists():
                try:
                    with open(system_config, 'r') as f:
                        sys_config = yaml.safe_load(f)
                        if sys_config:
                            config.update(sys_config)
                            self.log(f"已加载系统配置: {system_config}")
                except Exception as e:
                    self.log(f"加载系统配置失败: {e}", "WARN")

        self._config = config
        if not config:
            self.log("未找到任何配置，使用默认值", "WARN")
    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """深度合并字典"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default
    
    def update_config(self, updates: Dict) -> Any:
        """更新配置"""
        self._deep_merge(self._config, updates)
        config_file = self.config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False)
        self.log("配置已更新")
    
    # ==================== 生命周期 ====================
    
    def on_init(self) -> Any:
        """初始化钩子（子类可覆盖）"""
        pass
    
    def on_start(self) -> Any:
        """启动钩子（子类可覆盖）"""
        pass
    
    def on_stop(self) -> Any:
        """停止钩子（子类可覆盖）"""
        self._save_memory()
    
    def on_error(self, error: Exception) -> Any:
        """错误处理钩子（子类可覆盖）"""
        self.log(f"错误: {error}", "ERROR")
    
    # ==================== 工具方法 ====================
    
    def _update_stats(self) -> None:
        """更新统计信息"""
        if "stats" not in self._memory:
            self._memory["stats"] = {}
        self._memory["stats"]["last_active"] = datetime.now().isoformat()
        self._memory["stats"]["total_interactions"] = self._memory["stats"].get("total_interactions", 0) + 1
    
    def log(self, message: str, level: str = "INFO") -> Any:
        """日志输出"""
        print(f"[{self.name}] {level}: {message}")
    
    def get_status(self) -> Any:
        """获取 Agent 状态"""
        return {
            "name": self.name,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "version": self.VERSION,
            "type": self.type,
            "status": "running",
            "created_at": self.created_at.isoformat(),
            "last_active": self._memory.get("stats", {}).get("last_active"),
            "total_interactions": self._memory.get("stats", {}).get("total_interactions", 0)
        }
    
    def share_knowledge(self, target_agent: str, knowledge: Dict) -> bool:
        """
        分享知识给其他 Agent

        Args:
            target_agent: 目标 Agent 名称
            knowledge: 知识内容

        Returns:
            是否成功
        """
        try:
            from core.common.cross_learning import cross_learning
            return cross_learning.share_knowledge(self.name, target_agent, knowledge)
        except ImportError:
            self.log("跨区学习模块不可用", "WARN")
            return False
        except Exception as e:
            self.log(f"分享知识失败: {e}", "ERROR")
            return False
    
    def learn_from_others(self) -> List[Dict]:
        """从其他 Agent 学习"""
        try:
            from core.common.cross_learning import cross_learning
            return cross_learning.receive_knowledge(self.name)
        except:
            return []
    
    # ==================== 核心方法（子类必须实现） ====================
    def get_workspace_path(self) -> Any:
        """获取工作区路径"""
        from pathlib import Path
        workspace = Path(f"agents/{self.name}")
        if workspace.exists():
            return workspace
        return self.work_dir

    def get_user_id(self) -> None:
        """获取用户 ID"""
        return self.user_id

    def get_agent_name(self) -> None:
        """获取 Agent 名称"""
        return self.name

    def is_enabled(self) -> bool:
        """检查 Agent 是否启用"""
        return self.get_config("enabled", True)

    def get_capabilities(self) -> None:
        """获取能力列表"""
        return self.get_config("capabilities", [])

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """
        处理用户输入 - 子类必须实现

        Args:
            user_input: 用户输入
            context: 上下文信息（可选）

        Returns:
        {
                "success": bool,
                "response": str,
                "user_id": str,
                ...  # 其他自定义字段
            }
        """
        raise NotImplementedError("子类必须实现 process 方法")


def get_agent(agent_name: str, user_id: str = "default") -> Optional[BaseAgent]:
    """获取 Agent 实例（单例模式）"""
    key = f"{agent_name}_{user_id}"
    if key not in _agent_instances:
        try:
            module = __import__(f"core.agents.{agent_name}", fromlist=[agent_name])
            class_name = ''.join(word.capitalize() for word in agent_name.split('_')) + 'Agent'
            agent_class = getattr(module, class_name, None)
            if agent_class:
                _agent_instances[key] = agent_class(user_id=user_id)
        except Exception as e:
            print(f"获取 Agent {agent_name} 失败: {e}")
            return None
    return _agent_instances.get(key)

    
    def _init_inheritance(self) -> None:
        """初始化传承系统"""
        try:
            from core.inheritance.manager import InheritanceManager
            self.inheritance = InheritanceManager(self.user_id, self.name)
            self.log("传承系统已启动")
        except ImportError as e:
            self.log(f"传承系统不可用: {e}", "WARN")
    
    def learn_experience(self, exp_type: str, content: Dict, confidence: float = 0.5) -> Any:
        """学习经验"""
        if self.inheritance:
            return self.inheritance.learn(exp_type, content, confidence)
        return None
    
    def inherit_experience(self, parent_exp_id: str, adapter: Dict = None) -> Any:
        """继承经验"""
        if self.inheritance:
            parent_exp = self.inheritance.storage.get_experience(parent_exp_id)
            if parent_exp:
                return self.inheritance.inherit(parent_exp, adapter)
        return None
    
    def reinforce_experience(self, exp_id: str, success: bool) -> Any:
        """强化经验"""
        if self.inheritance:
            self.inheritance.reinforce(exp_id, success)
    
    def get_best_experience(self, exp_type: str = None) -> Any:
        """获取最佳经验"""
        if self.inheritance:
            return self.inheritance.get_best(exp_type)
        return None


    def _init_inheritance_config_driven(self) -> None:
        """配置驱动的传承系统初始化"""
        import yaml
        from pathlib import Path

        config_file = Path("config/inheritance.yaml")
        if not config_file.exists():
            return

        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)

            if not config.get('enabled', True):
                self.log("传承系统已禁用", "INFO")
                return

            from core.inheritance.manager import InheritanceManager
            self.inheritance = InheritanceManager(self.user_id, self.name)
            self.log("传承系统已启动（配置驱动）")
        except ImportError as e:
            self.log(f"传承系统模块不可用: {e}", "WARN")
        except Exception as e:
            self.log(f"传承系统初始化失败: {e}", "ERROR")
    
    def learn_experience(self, exp_type: str, content: Dict, confidence: float = 0.5) -> Any:
        """学习经验 - 配置驱动"""
        if not hasattr(self, 'inheritance') or not self.inheritance:
            return None
        return self.inheritance.learn(exp_type, content, confidence)
    
    def inherit_experience(self, parent_exp_id: str, adapter: Dict = None) -> Any:
        """继承经验 - 配置驱动"""
        if not hasattr(self, 'inheritance') or not self.inheritance:
            return None
        parent_exp = self.inheritance.storage.get_experience(parent_exp_id)
        if parent_exp:
            return self.inheritance.inherit(parent_exp, adapter)
        return None

    # ==================== 补充方法 ====================

    def get_workspace_path(self) -> Path:
        """获取 Agent 工作区路径（配置驱动）"""
        # 优先使用工作区目录
        workspace = Path(f"agents/{self.name}")
        if workspace.exists():
            return workspace
        # 回退到用户目录
        return self.work_dir

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """获取配置值（支持点号路径）"""
        return self.get_config(key, default)

    def update_user_config(self, updates: Dict) -> bool:
        """更新用户配置（持久化）"""
        try:
            self._deep_merge(self._config, updates)
            config_file = self.config_dir / "config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False)
            self.log("用户配置已更新")
            return True
        except Exception as e:
            self.log(f"更新配置失败: {e}", "ERROR")
            return False

    def get_user_id(self) -> None:
        """获取用户 ID"""
        return self.user_id

    def get_agent_name(self) -> None:
        """获取 Agent 名称"""
        return self.name

    def is_enabled(self) -> bool:
        """检查 Agent 是否启用"""
        return self.get_config("enabled", True)

    def get_capabilities(self) -> List[str]:
        """获取 Agent 能力列表"""
        return self.get_config("capabilities", [])



    # ========== 通信记录 ==========

    def save_communication(self, to_agent: str, request: str, response: dict, duration_ms: float = 0) -> Any:
        """保存 Agent 间通信记录"""
        import json
        from datetime import datetime
        from pathlib import Path

        record = {
            "timestamp": datetime.now().isoformat(),
            "from": self.name,
            "to": to_agent,
            "request": request,
            "response": response,
            "duration_ms": duration_ms,
            "user_id": self.user_id
        }

        log_dir = Path("data/exchange")
        log_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        with open(log_dir / filename, 'w') as f:
            json.dump(record, f, indent=2)
        print(f"[记录] {self.name} -> {to_agent}: {filename}")

    # ========== 通信记录（基类方法，所有 Agent 继承） ==========

    def record_communication(self, to_agent: str, request: str, response: dict, duration_ms: float = 0) -> Any:
        """记录 Agent 间通信（基类方法）"""
        import json
        from datetime import datetime
        from pathlib import Path

        record = {
            "timestamp": datetime.now().isoformat(),
            "from": self.name,
            "to": to_agent,
            "request": request,
            "response": response,
            "duration_ms": duration_ms,
            "user_id": self.user_id
        }

        log_dir = Path("data/exchange")
        log_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        with open(log_dir / filename, 'w') as f:
            json.dump(record, f, indent=2)

        return filename

    def send_and_record(self, to_agent: str, message: str) -> None:
        """发送消息并自动记录"""
        import time
        import requests

        start = time.time()
        resp = requests.post(
            f"http://{unified_config.get("services.gateway.host", "localhost")}:{unified_config.get("services.gateway.port", 5002)}/api/agent/{to_agent}/message",
            json={"message": message, "user_id": self.user_id},
            timeout=10
        )
        duration_ms = (time.time() - start) * 1000

        result = resp.json() if resp.status_code == 200 else {"error": f"HTTP {resp.status_code}"}

        # 自动记录
        self.record_communication(to_agent, message, result, duration_ms)

        return result


        return result

    # 全局实例管理
_agent_instances: Dict[str, BaseAgent] = {}
