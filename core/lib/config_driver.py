#!/usr/bin/env python3
"""配置驱动核心 - 向后兼容接口"""

from lib.config_loader import config

# 导出兼容接口
__all__ = ['config_driver']


class ConfigDriverCompatible:
    """向后兼容的配置驱动接口"""
    
    @property
    def VERSION(self):
        return config.VERSION
    
    def get(self, key, default=None):
        return config.get(key, default)
    
    def get_port(self, service):
        return config.get_port(service)
    
    def get_path(self, name):
        return config.get_path(name)
    
    def is_enabled(self, feature):
        return config.is_enabled(feature)
    
    def reload(self):
        config.reload()
    
    def get_status(self):
        return config.get_status()


config_driver = ConfigDriverCompatible()


if __name__ == "__main__":
    print(f"配置驱动 v{config_driver.VERSION}")
    print(f"gateway 端口: {config_driver.get_port('gateway')}")
    print(f"质量阈值: {config_driver.get('thresholds.quality_min_score')}")
    print(f"智能调度启用: {config_driver.is_enabled('enable_smart_scheduling')}")
