"""工作区管理器 - 统一管理 Agent 工作区"""

import json
from pathlib import Path
from datetime import datetime

class WorkspaceManager:
    def __init__(self, base_path="agents"):
        self.base_path = Path(base_path)
    
    def get_workspace(self, agent_id):
        """获取 Agent 工作区路径"""
        ws_path = self.base_path / f"{agent_id}_ws"
        ws_path.mkdir(parents=True, exist_ok=True)
        return ws_path
    
    def get_config(self, agent_id):
        """获取 Agent 配置"""
        config_file = self.get_workspace(agent_id) / "config/config.yaml"
        if config_file.exists():
            import yaml
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def save_memory(self, agent_id, memory_data):
        """保存 Agent 记忆"""
        memory_file = self.get_workspace(agent_id) / "memory/memory.json"
        with open(memory_file, 'w') as f:
            json.dump(memory_data, f, indent=2)
        return True
    
    def load_memory(self, agent_id):
        """加载 Agent 记忆"""
        memory_file = self.get_workspace(agent_id) / "memory/memory.json"
        if memory_file.exists():
            with open(memory_file, 'r') as f:
                return json.load(f)
        return {"memories": []}
    
    def list_workspaces(self):
        """列出所有工作区"""
        return [d.name for d in self.base_path.glob("*_ws") if d.is_dir()]

workspace_manager = WorkspaceManager()
