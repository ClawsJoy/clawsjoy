"""config - unified_config 代理"""
from core.lib.unified_config import unified_config


class Config:
    def get(self, path: str = None, default=None):
        if path is None:
            return unified_config.get("config", {})
        return unified_config.get(f"config.{path}", default)


config = Config()
