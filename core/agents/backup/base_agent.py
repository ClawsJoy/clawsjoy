"""Agent 基类 - 支持工作区、记忆、人格"""

import yaml
from pathlib import Path
from lib.memory_simple import memory
from lib.workspace_manager import workspace_manager

class BaseAgent:
    def __init__(self, agent_id, config=None):
        self.agent_id = agent_id
        self.config = config or self._load_config()
        self.name = self.config.get('name', agent_id)
        self.type = self.config.get('type', 'custom')
        self.capabilities = self.config.get('capabilities', [])
        
        # 工作区
        self.workspace = workspace_manager.get_workspace(agent_id)
        self.personality = self._load_personality()
        self._load_agent_memory()
        
        print(f"✅ Agent 初始化: {self.name} ({self.type})")
    
    def _load_config(self):
        config_file = Path("config/agents.yaml")
        if config_file.exists():
            import yaml
            with open(config_file, 'r') as f:
                all_config = yaml.safe_load(f)
                return all_config.get('agents', {}).get(self.agent_id, {})
        return {}
    
    def _load_personality(self):
        persona_name = self.config.get('personality', 'default')
        persona_file = Path(f"agents/personalities/{persona_name}.yaml")
        if persona_file.exists():
            import yaml
            with open(persona_file, 'r') as f:
                return yaml.safe_load(f)
        return {'style': 'professional', 'language': 'zh-CN', 'tone': 'formal'}
    
    def _load_agent_memory(self):
        """加载 Agent 私有记忆"""
        self.agent_memory = workspace_manager.load_memory(self.agent_id)
        if not self.agent_memory.get('memories'):
            self.agent_memory = {'memories': [], 'agent': self.agent_id}
    
    def _save_agent_memory(self):
        """保存 Agent 私有记忆"""
        workspace_manager.save_memory(self.agent_id, self.agent_memory)
    
    def remember(self, content, shared=True):
        """记录记忆"""
        if shared:
            # 共享记忆
            memory.remember(f"[{self.name}] {content}", category="agent_memory")
        else:
            # 私有记忆
            self.agent_memory['memories'].append({
                'time': __import__('datetime').datetime.now().isoformat(),
                'content': content
            })
            self._save_agent_memory()
    
    def recall(self, query=None, n=5):
        """回忆记忆"""
        if query:
            return memory.recall(query, n=n)
        return self.agent_memory.get('memories', [])[-n:]
    
    def get_greeting(self):
        """获取问候语"""
        greeting = self.personality.get('greeting', f"你好，我是 {self.name}")
        return greeting.format(name=self.name)
    
    def execute(self, params):
        raise NotImplementedError("子类必须实现 execute 方法")

from lib.memory_layers import memory_layers

class BaseAgent:
    # ... 原有代码 ...
    
    def add_memory(self, content, memory_type="session"):
        """添加记忆到指定层"""
        if memory_type == "session":
            return memory_layers.add_session_memory(self.agent_id, "", content)
        elif memory_type == "daily":
            return memory_layers.add_daily_memory(f"[{self.name}] {content}")
        elif memory_type == "long_term":
            return memory_layers.add_long_term_memory(f"[{self.name}] {content}")
        elif memory_type == "vector":
            return memory_layers.add_vector_memory(content, category=self.agent_id)
        return False
    
    def search_memory(self, query, layers=["vector"]):
        """搜索记忆"""
        results = []
        if "vector" in layers:
            results.extend(memory_layers.search_vector_memory(query, n=5))
        if "long_term" in layers:
            results.extend(memory_layers.get_long_term_memory(limit=5))
        return results

from lib.memory_layers import memory_layers

class BaseAgent:
    # ... 原有代码 ...
    
    def add_memory(self, content, memory_type="session"):
        """添加记忆到指定层"""
        if memory_type == "session":
            return memory_layers.add_session_memory(self.agent_id, "", content)
        elif memory_type == "daily":
            return memory_layers.add_daily_memory(f"[{self.name}] {content}")
        elif memory_type == "long_term":
            return memory_layers.add_long_term_memory(f"[{self.name}] {content}")
        elif memory_type == "vector":
            return memory_layers.add_vector_memory(content, category=self.agent_id)
        return False
    
    def search_memory(self, query, layers=["vector"]):
        """搜索记忆"""
        results = []
        if "vector" in layers:
            results.extend(memory_layers.search_vector_memory(query, n=5))
        if "long_term" in layers:
            results.extend(memory_layers.get_long_term_memory(limit=5))
        return results

from lib.memory_layers import memory_layers

class BaseAgent:
    # ... 原有代码 ...
    
    def add_memory(self, content, memory_type="session"):
        """添加记忆到指定层"""
        if memory_type == "session":
            return memory_layers.add_session_memory(self.agent_id, "", content)
        elif memory_type == "daily":
            return memory_layers.add_daily_memory(f"[{self.name}] {content}")
        elif memory_type == "long_term":
            return memory_layers.add_long_term_memory(f"[{self.name}] {content}")
        elif memory_type == "vector":
            return memory_layers.add_vector_memory(content, category=self.agent_id)
        return False
    
    def search_memory(self, query, layers=["vector"]):
        """搜索记忆"""
        results = []
        if "vector" in layers:
            results.extend(memory_layers.search_vector_memory(query, n=5))
        if "long_term" in layers:
            results.extend(memory_layers.get_long_term_memory(limit=5))
        return results
