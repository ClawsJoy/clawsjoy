"""service_config - unified_config 代理"""
from core.lib.unified_config import unified_config


class Service_config:
    def get(self, path: str = None, default=None):
        if path is None:
            return unified_config.get("service_config", {})
        return unified_config.get(f"service_config.{path}", default)


service_config = Service_config()
