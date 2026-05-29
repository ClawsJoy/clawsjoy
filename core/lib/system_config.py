"""system_config - unified_config 代理"""
from core.lib.unified_config import unified_config


class System_config:
    def get(self, path: str = None, default=None):
        if path is None:
            return unified_config.get("system_config", {})
        return unified_config.get(f"system_config.{path}", default)


system_config = System_config()
