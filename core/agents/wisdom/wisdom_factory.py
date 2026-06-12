#!/usr/bin/env python3
"""智慧 Agent 工厂 - 批量智慧化改造"""

from typing import Dict, Optional


class WisdomFactory:
    """智慧 Agent 工厂"""
    
    _instance = None
    _wrapped_agents: Dict[str, object] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def create_wisdom_agent(self, agent, config: Dict = None):
        """创建智慧包装的 Agent"""
        from core.agents.wisdom.wisdom_wrapper import WisdomWrapper
        
        agent_name = getattr(agent, 'name', 'unknown')
        
        if agent_name in self._wrapped_agents:
            return self._wrapped_agents[agent_name]
        
        wrapper = WisdomWrapper(agent, config)
        self._wrapped_agents[agent_name] = wrapper
        
        return wrapper
    
    def get_wisdom_agent(self, agent_name: str, user_id: str = "default"):
        """获取已创建的智慧 Agent"""
        key = f"{agent_name}:{user_id}"
        
        if key in self._wrapped_agents:
            return self._wrapped_agents[key]
        
        # 动态加载 Agent
        agent = self._load_agent(agent_name, user_id)
        if agent:
            from core.agents.wisdom.wisdom_wrapper import WisdomWrapper
            self._wrapped_agents[key] = WisdomWrapper(agent)
            return self._wrapped_agents[key]
        
        return None
    
    def _load_agent(self, agent_name: str, user_id: str):
        """动态加载 Agent"""
        try:
            # 优先使用 V4 版本（智慧化试点）
            if agent_name == "chat_agent":
                from agents.chat_agent.agent_v4 import ChatAgentV4
                print(f"✅ 加载 {agent_name} V4 智慧版本")
                return ChatAgentV4(user_id)
            if agent_name == "code_agent":
                from agents.code_agent.agent_v4 import CodeAgentV4
                print(f"✅ 加载 {agent_name} V4 智慧版本")
                return CodeAgentV4(user_id)            
            # 其他 Agent 使用原有加载逻辑
            module = __import__(f"agents.{agent_name}.agent", fromlist=[agent_name])
            for attr in dir(module):
                if attr.endswith("Agent"):
                    agent_class = getattr(module, attr)
                    # 检查是否为抽象类
                    if not getattr(agent_class, '__abstractmethods__', False):
                        print(f"✅ 加载 {agent_name} 原始版本")
                        return agent_class(user_id)
        except Exception as e:
            print(f"❌ 加载 Agent {agent_name} 失败: {e}")
        return None
    
    def get_all_wisdom_stats(self) -> Dict:
        """获取所有智慧 Agent 统计"""
        return {
            name: wrapper.get_self_awareness()
            for name, wrapper in self._wrapped_agents.items()
        }


wisdom_factory = WisdomFactory()
