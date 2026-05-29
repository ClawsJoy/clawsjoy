"""llm_config - unified_config 代理"""
from core.lib.unified_config import unified_config


class Llm_config:
    def get(self, path: str = None, default=None):
        if path is None:
            return unified_config.get("llm_config", {})
        return unified_config.get(f"llm_config.{path}", default)


llm_config = Llm_config()
