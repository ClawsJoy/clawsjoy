"""clawsjoy_config - unified_config 代理"""
from core.lib.unified_config import unified_config


class Clawsjoy_config:
    def get(self, path: str = None, default=None):
        if path is None:
            return unified_config.get("clawsjoy_config", {})
        return unified_config.get(f"clawsjoy_config.{path}", default)


clawsjoy_config = Clawsjoy_config()
