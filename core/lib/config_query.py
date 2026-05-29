from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""配置查询模块"""

from pathlib import Path
from core.lib.constants import PROJECT_ROOT

class ConfigQuery:
    def __init__(self):
        self.config_dir = PROJECT_ROOT / "config"
    
    def get(self, key: str, default=None):
        # 简化实现
        return default

config_query = ConfigQuery()
# DEPRECATED: 请使用 unified_config 代替
