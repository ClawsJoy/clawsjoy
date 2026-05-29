from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""Agent 管理器 - 统一管理所有 Agent 的生命周期"""

import yaml
from pathlib import Path
from core.lib.agent_registry import agent_registry
from core.lib.workspace_manager import workspace_manager
from core.lib.config_manager import config_manager
from core.lib.unified_config import unified_config

class AgentManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        # 加载 Agent 配置
        self.config_file = Path("config/agents/registry/agents.yaml")
        self.agents = self._load_agents()
        
        # 注册到注册中心
        for agent_id, info in self.agents.items():
            agent_registry.register(agent_id, info)
        
        print(f"✅ Agent 管理器初始化完成，共 {len(self.agents)} 个 Agent")
    
    def _load_agents(self):
        """从配置文件加载 Agent"""
        import yaml
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f)
                # 支持两种格式：直接列表 或 agents: 下的列表
                if data and 'agents' in data:
                    return data['agents']
                return data if isinstance(data, dict) else {}
        return self._get_default_agents()
    
    def _get_default_agents(self):
        """默认 Agent 配置"""
        return {
            'orchestrator': {
                'name': '任务编排器', 'type': 'core',
                'capabilities': ['task_planning', 'skill_orchestration'],
                'personality': 'professional', 'port': 5002
            },
            'code_agent': {
                'name': '代码助手', 'type': 'custom',
                'capabilities': ['code_generation', 'code_review'],
                'personality': 'technical'
            },
            'video_agent': {
                'name': '视频制作助手', 'type': 'custom',
                'capabilities': ['video_creation', 'manju_maker'],
                'personality': 'creative'
            },
            'youtube_agent': {
                'name': 'YouTube助手', 'type': 'custom',
                'capabilities': ['video_upload', 'channel_analysis']
            },
            'security_agent': {
                'name': '安全助手', 'type': 'core',
                'capabilities': ['security_check', 'permission_verify']
            },
            'memory_manager': {
                'name': '记忆管理助手', 'type': 'core',
                'capabilities': ['memory_store', 'memory_recall']
            }
        }
    
    def list_agents(self):
        return list(self.agents.keys())
    
    def get_agent(self, name):
        return self.agents.get(name)
    
    def get_agents_by_type(self, agent_type):
        return [name for name, info in self.agents.items() if info.get('type') == agent_type]
    
    def get_stats(self):
        return {
            'total': len(self.agents),
            'core': len(self.get_agents_by_type('core')),
            'custom': len(self.get_agents_by_type('custom')),
            'workspaces': len(workspace_manager.list_workspaces()),
            'registry': agent_registry.get_stats()
        }
    
    def reload(self):
        """重新加载 Agent 配置"""
        self._init()
        return True

agent_manager = AgentManager()

