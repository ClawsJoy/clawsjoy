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
    
    def register(self, name, capabilities, skills=None, version="1.0.0", description=""):
        """注册 Agent"""
        self.agents[name] = {
            "name": name,
            "capabilities": capabilities,
            "skills": skills or [],
            "version": version,
            "description": description,
            "status": "active",
            "registered_at": datetime.now().isoformat()
        }
        self._save()
        print(f"✅ Agent 已注册: {name} v{version}")
        return True
    
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
agent_registry.register(
    name='code_agent',
    capabilities=['code_generation', 'code_review'],
    skills=['code_agent_v7'],
    version='1.0.0',
    description='代码生成和审查 Agent'
)

agent_registry.register(
    name='video_agent',
    capabilities=['video_creation', 'video_upload'],
    skills=['manju_maker', 'video_uploader'],
    version='1.0.0',
    description='视频制作 Agent'
)

agent_registry.register(
    name='youtube_agent',
    capabilities=['youtube_analyze', 'youtube_upload'],
    skills=['hot_analyzer'],
    version='1.0.0',
    description='YouTube 运营 Agent'
)

print(f"✅ Agent 注册中心已初始化，共 {len(agent_registry.list_all())} 个 Agent")
