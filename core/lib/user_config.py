"""user_config - unified_config 代理"""
from core.lib.unified_config import unified_config


class User_config:
    def get(self, path: str = None, default=None):
        if path is None:
            return unified_config.get("user_config", {})
        return unified_config.get(f"user_config.{path}", default)


user_config = User_config()
