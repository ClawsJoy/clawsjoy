"""layered_config - unified_config 代理"""
from core.lib.unified_config import unified_config


class Layered_config:
    def get(self, path: str = None, default=None):
        if path is None:
            return unified_config.get("layered_config", {})
        return unified_config.get(f"layered_config.{path}", default)


layered_config = Layered_config()
