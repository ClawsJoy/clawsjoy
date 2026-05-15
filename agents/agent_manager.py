import json
from pathlib import Path

class AgentManager:
    def __init__(self):
        self.agents = {}
        self._load_core_agents()
        self._load_custom_agents()
    
    def _load_core_agents(self):
        """加载 Core Agent"""
        core_dir = Path("core")
        if not core_dir.exists():
            return
        
        for ws_dir in core_dir.glob("*_ws"):
            if ws_dir.is_dir():
                agent_name = ws_dir.name.replace("_ws", "")
                self.agents[agent_name] = {
                    "type": "core",
                    "config": self._load_json(ws_dir / "config.json"),
                    "memory": self._load_json(ws_dir / "memory.json"),
                    "workspace": ws_dir / "workspace"
                }
                print(f"✅ 加载 Core Agent: {agent_name}")
    
    def _load_custom_agents(self):
        """加载 Custom Agent"""
        custom_dir = Path("custom")
        if not custom_dir.exists():
            return
        
        for agent_dir in custom_dir.iterdir():
            if agent_dir.is_dir():
                agent_name = agent_dir.name
                self.agents[agent_name] = {
                    "type": "custom",
                    "config": self._load_json(agent_dir / "config.json"),
                    "memory": self._load_json(agent_dir / "memory.json"),
                    "workspace": agent_dir / "workspace"
                }
                print(f"✅ 加载 Custom Agent: {agent_name}")
    
    def _load_json(self, path):
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {}
    
    def get_agent(self, name):
        return self.agents.get(name)
    
    def list_agents(self):
        return list(self.agents.keys())
    
    def get_stats(self):
        return {
            "total": len(self.agents),
            "core": len([a for a in self.agents.values() if a["type"] == "core"]),
            "custom": len([a for a in self.agents.values() if a["type"] == "custom"])
        }

if __name__ == "__main__":
    manager = AgentManager()
    print(f"\n📊 Agent 统计: {manager.get_stats()}")
    print(f"📋 Agent 列表: {manager.list_agents()}")
