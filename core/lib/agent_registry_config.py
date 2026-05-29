"""agent_registry_config - unified_config 代理"""
from core.lib.unified_config import unified_config


class Agent_registry_config:
    def get(self, path: str = None, default=None):
        if path is None:
            return unified_config.get("agent_registry_config", {})
        return unified_config.get(f"agent_registry_config.{path}", default)


agent_registry_config = Agent_registry_config()
