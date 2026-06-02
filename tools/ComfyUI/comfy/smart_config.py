#!/usr/bin/env python3
"""临时 smart_config 模块 - 绕过导入错误"""

class SmartConfig:
    """简化版配置类"""
    def __init__(self):
        self._config = {}
    
    def get(self, key, default=None):
        return self._config.get(key, default)
    
    def __getattr__(self, name):
        return self._config.get(name, None)

smart_config = SmartConfig()
