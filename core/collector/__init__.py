"""采集管理中心 - 安全合规采集"""
from .manager import CollectorManager
from .safety import SafetyChecker

# 创建全局实例
from .manager import collector_manager

__all__ = ['CollectorManager', 'SafetyChecker', 'collector_manager']
