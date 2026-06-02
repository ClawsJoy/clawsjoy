#!/usr/bin/env python3
"""Agent Router - Agent Router 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
"""Agent 路由器 - 配置驱动，安全隔离"""
import yaml
from pathlib import Path


class AgentRouter:
    """Agent 路由器"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        config_file = Path(__file__).parent.parent / "config/agent_routing.yaml"
        if config_file.exists():
            with open(config_file, 'r') as f:
                self._config = unified_config.get("router")
        else:
            self._config = {"routing": {}}
    
    def get_agent(self, user_role='guest'):
        """根据用户角色获取对应的 Agent"""
        routing = self._config.get('routing', {})
        route = routing.get(user_role, routing.get('guest', {}))
        agent_name = route.get('agent', 'chat_agent')

        if agent_name == 'personal_butler':
            from core.agents.builtin.personal_butler_v2 import PersonalButlerV2
            personal_butler = PersonalButlerV2()
            return personal_butler
        else:
            from core.agents.builtin.chat_agent import chat_agent
            return chat_agent
    
    def get_config(self, user_role='guest'):
        """获取用户角色的配置"""
        routing = self._config.get('routing', {})
        return routing.get(user_role, routing.get('guest', {}))


agent_router = AgentRouter()
