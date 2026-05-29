"""闭环流程配置 - unified_config 代理"""
from core.lib.unified_config import unified_config


class ClosedLoopConfig:
    """配置代理 - 从 unified_config 读取"""

    def get(self, path: str = None, default=None):
        if path is None:
            return unified_config.get("closed_loop", {})
        return unified_config.get(f"closed_loop.{path}", default)


closed_loop_config = ClosedLoopConfig()
