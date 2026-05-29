"""Agent生命周期配置 - unified_config 代理"""
from core.lib.unified_config import unified_config


class AgentLifecycleConfig:
    def get(self, path: str = None, default=None):
        if path is None:
            return unified_config.get("agent_lifecycle", {})
        return unified_config.get(f"agent_lifecycle.{path}", default)


agent_lifecycle_config = AgentLifecycleConfig()
