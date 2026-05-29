"""memory_optimization_config - unified_config 代理"""
from core.lib.unified_config import unified_config


class Memory_optimization_config:
    def get(self, path: str = None, default=None):
        if path is None:
            return unified_config.get("memory_optimization_config", {})
        return unified_config.get(f"memory_optimization_config.{path}", default)


memory_optimization_config = Memory_optimization_config()
