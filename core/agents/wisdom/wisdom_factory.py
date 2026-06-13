#!/usr/bin/env python3
"""智慧 Agent 工厂 - 集成版（兼容现有注册中心、懒加载）"""

from typing import Dict, Optional
from core.lib.lazy_loader import lazy_loader
from core.lib.agent_registry import agent_registry


class WisdomFactory:
    """智慧 Agent 工厂 - 集成现有基础设施"""

    _instance = None
    _wrapped_agents: Dict[str, object] = {}
    _agent_cache: Dict[str, object] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """初始化：注册 V4 Agent 到懒加载器"""
        print("🧠 WisdomFactory 初始化（集成模式）")
        
        # 将 V4 Agent 注册到懒加载器
        self._register_v4_agents_to_lazy()
        
        # 同步到 agent_registry
        self._sync_to_registry()

    def _register_v4_agents_to_lazy(self):
        """将 V4 Agent 注册到懒加载器"""
        
        v4_agents = {
            "chat_agent": ("agents.chat_agent.agent_v4", "ChatAgentV4"),
            "code_agent": ("agents.code_agent.agent_v4", "CodeAgentV4"),
            "analysis_agent": ("agents.analysis_agent.agent_v4", "AnalysisAgentV4"),
            "butler_agent": ("agents.butler_agent.agent_v4", "ButlerAgentV4"),
            "translate_agent": ("agents.translate_agent.agent_v4", "TranslateAgentV4"),
            "calculator_agent": ("agents.calculator_agent.agent_v4", "CalculatorAgentV4"),
            "orchestrator": ("agents.orchestrator.agent_v4", "OrchestratorV4"),
            "decision_agent": ("agents.decision_agent.agent_v4", "DecisionAgentV4"),
        }

        for agent_name, (module_path, class_name) in v4_agents.items():
            def make_loader(mod_path, cls_name):
                def loader():
                    try:
                        module = __import__(mod_path, fromlist=[cls_name])
                        agent_class = getattr(module, cls_name)
                        return agent_class
                    except Exception as e:
                        print(f"❌ 懒加载 {mod_path} 失败: {e}")
                        return None
                return loader

            lazy_loader.register(f"{agent_name}_v4", make_loader(module_path, class_name))
            print(f"  📦 注册懒加载: {agent_name}_v4")

    def _sync_to_registry(self):
        """同步 V4 Agent 到 agent_registry"""
        v4_agent_names = [
            "chat_agent", "code_agent", "analysis_agent", "butler_agent",
            "translate_agent", "calculator_agent", "orchestrator", "decision_agent"
        ]
        
        for agent_name in v4_agent_names:
            if agent_name not in agent_registry.agents:
                agent_registry.register(agent_name, {
                    "name": agent_name,
                    "type": "v4_wisdom",
                    "version": "4.0.0",
                    "description": f"智慧化 {agent_name}",
                    "capabilities": self._get_agent_capabilities(agent_name),
                    "status": "active"
                })
                print(f"  📋 同步到注册中心: {agent_name}")

    def _get_agent_capabilities(self, agent_name: str) -> list:
        """获取 Agent 能力描述"""
        capabilities = {
            "chat_agent": ["chat", "对话", "记忆", "情感", "主动建议"],
            "code_agent": ["code", "代码生成", "调试", "优化", "测试"],
            "analysis_agent": ["analysis", "数据分析", "统计", "报告"],
            "butler_agent": ["butler", "待办", "提醒", "日程"],
            "translate_agent": ["translate", "翻译", "多语言"],
            "calculator_agent": ["calculate", "计算", "科学计算"],
            "orchestrator": ["orchestrate", "编排", "调度", "分解"],
            "decision_agent": ["decision", "决策", "路由", "评估"],
        }
        return capabilities.get(agent_name, [])

    def get_wisdom_agent(self, agent_name: str, user_id: str = "default"):
        """获取智慧 Agent（支持懒加载）"""
        key = f"{agent_name}:{user_id}"
        
        # 检查缓存
        if key in self._wrapped_agents:
            return self._wrapped_agents[key]
        
        # 从懒加载器获取
        agent_class = None
        lazy_key = f"{agent_name}_v4"
        
        if lazy_loader.is_loaded(lazy_key):
            agent_class = lazy_loader.get(lazy_key)
        
        # 降级：使用原有加载逻辑
        if not agent_class:
            agent_class = self._legacy_load_agent(agent_name)
        
        if agent_class:
            # 实例化 Agent
            agent = agent_class(user_id)
            
            # 包装为智慧包装器
            from core.agents.wisdom.wisdom_wrapper import WisdomWrapper
            self._wrapped_agents[key] = WisdomWrapper(agent)
            return self._wrapped_agents[key]
        
        return None

    def _legacy_load_agent(self, agent_name: str):
        """降级加载（兼容原有逻辑）"""
        try:
            # 直接导入 V4 版本
            v4_imports = {
                "chat_agent": ("agents.chat_agent.agent_v4", "ChatAgentV4"),
                "code_agent": ("agents.code_agent.agent_v4", "CodeAgentV4"),
                "analysis_agent": ("agents.analysis_agent.agent_v4", "AnalysisAgentV4"),
                "butler_agent": ("agents.butler_agent.agent_v4", "ButlerAgentV4"),
                "translate_agent": ("agents.translate_agent.agent_v4", "TranslateAgentV4"),
                "calculator_agent": ("agents.calculator_agent.agent_v4", "CalculatorAgentV4"),
                "orchestrator": ("agents.orchestrator.agent_v4", "OrchestratorV4"),
                "decision_agent": ("agents.decision_agent.agent_v4", "DecisionAgentV4"),
            }
            
            if agent_name in v4_imports:
                module_path, class_name = v4_imports[agent_name]
                module = __import__(module_path, fromlist=[class_name])
                return getattr(module, class_name)
            
            # 原始 Agent 加载
            module = __import__(f"agents.{agent_name}.agent", fromlist=[agent_name])
            for attr in dir(module):
                if attr.endswith("Agent"):
                    agent_class = getattr(module, attr)
                    if not getattr(agent_class, '__abstractmethods__', False):
                        return agent_class
        except Exception as e:
            print(f"❌ 降级加载 {agent_name} 失败: {e}")
        
        return None

    def reload_agent(self, agent_name: str, user_id: str = "default") -> bool:
        """热重载 Agent"""
        key = f"{agent_name}:{user_id}"
        
        # 清除缓存
        if key in self._wrapped_agents:
            del self._wrapped_agents[key]
        
        # 清除懒加载缓存
        lazy_key = f"{agent_name}_v4"
        if lazy_loader.is_loaded(lazy_key):
            lazy_loader.reload(lazy_key)
        
        print(f"🔄 热重载 Agent: {agent_name}")
        return True

    def create_wisdom_agent(self, agent, config: Dict = None):
        """创建智慧包装的 Agent（兼容原接口）"""
        from core.agents.wisdom.wisdom_wrapper import WisdomWrapper

        agent_name = getattr(agent, 'name', 'unknown')

        if agent_name in self._wrapped_agents:
            return self._wrapped_agents[agent_name]

        wrapper = WisdomWrapper(agent, config)
        self._wrapped_agents[agent_name] = wrapper
        return wrapper

    def get_all_wisdom_stats(self) -> Dict:
        """获取所有智慧 Agent 统计"""
        stats = {
            "wrapped_agents": len(self._wrapped_agents),
            "agents": {}
        }
        
        for name, wrapper in self._wrapped_agents.items():
            if hasattr(wrapper, 'get_self_awareness'):
                stats["agents"][name] = wrapper.get_self_awareness()
        
        # 合并注册中心统计
        stats["registry"] = agent_registry.get_stats()
        stats["lazy_loaded"] = [k for k in lazy_loader._loaded.keys() if "agent" in k]
        
        return stats


wisdom_factory = WisdomFactory()
