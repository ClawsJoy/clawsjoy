"""Agent 注册中心 V2 - 简化版"""
import json
from pathlib import Path
from datetime import datetime

class AgentRegistryV2:
    def __init__(self, registry_file="data/agent_registry_v2.json"):
        self.registry_file = Path(registry_file)
        self.agents = {}
        self._load()
    
    def _load(self):
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                self.agents = json.load(f)
    
    def _save(self):
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(self.agents, f, indent=2)
    
    def register(self, name, capabilities, skills=None, version="1.0.0"):
        self.agents[name] = {
            "name": name, "capabilities": capabilities, "skills": skills or [],
            "version": version, "status": "active",
            "registered_at": datetime.now().isoformat()
        }
        self._save()
    
    def get(self, name):
        return self.agents.get(name)
    
    def list_all(self):
        return list(self.agents.keys())
    
    def find_by_capability(self, capability):
        return [a for a in self.agents.values() if capability in a.get("capabilities", [])]
    
    def route_request(self, capability):
        agents = self.find_by_capability(capability)
        return agents[0]["name"] if agents else None
    
    def get_stats(self):
        active = len([a for a in self.agents.values() if a.get("status") == "active"])
        return {"total": len(self.agents), "active": active, "agents": self.agents}

agent_registry = AgentRegistryV2()

# 注册内置 Agent
agent_registry.register("code_agent", ["code_generation", "code_review"], ["code_agent_v7"])
agent_registry.register("video_agent", ["video_creation", "video_upload"], ["manju_maker", "video_uploader"])
agent_registry.register("youtube_agent", ["youtube_analyze", "youtube_upload"], ["hot_analyzer"])
