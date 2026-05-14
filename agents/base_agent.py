"""Agent 基类 - 支持工作区隔离"""
import json
import os
from pathlib import Path

class BaseAgent:
    """所有 Agent 的基类"""
    
    def __init__(self, agent_name, agent_type="custom"):
        self.agent_name = agent_name
        self.agent_type = agent_type  # "core" or "custom"
        
        # 确定工作区路径
        if agent_type == "core":
            self.workspace_dir = Path(f"agents/core/{agent_name}_ws")
        else:
            self.workspace_dir = Path(f"agents/custom/{agent_name}")
        
        self.config_file = self.workspace_dir / "config.json"
        self.memory_file = self.workspace_dir / "memory.json"
        self.work_dir = self.workspace_dir / "workspace"
        
        # 确保目录存在
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载配置和记忆
        self.config = self._load_config()
        self.memory = self._load_memory()
    
    def _load_config(self):
        """加载 Agent 配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            "name": self.agent_name,
            "personality": {"style": "professional", "language": "zh-CN"}
        }
    
    def _load_memory(self):
        """加载 Agent 记忆"""
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {"conversations": [], "learned_preferences": {}}
    
    def save_memory(self):
        """保存记忆"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def remember(self, key, value):
        """记住信息"""
        self.memory["learned_preferences"][key] = value
        self.save_memory()
    
    def recall(self, key):
        """回忆信息"""
        return self.memory["learned_preferences"].get(key)
    
    def get_personality(self):
        """获取个性配置"""
        return self.config.get("personality", {})
    
    def log_conversation(self, user_input, response):
        """记录对话历史"""
        self.memory["conversations"].append({
            "user": user_input,
            "assistant": response,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        # 保留最近 50 条
        if len(self.memory["conversations"]) > 50:
            self.memory["conversations"] = self.memory["conversations"][-50:]
        self.save_memory()
