#!/usr/bin/env python3
"""Init - Init 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from .manager import CollectorManager
from .safety import SafetyChecker

# 创建全局实例
from .manager import collector_manager

__all__ = ['CollectorManager', 'SafetyChecker', 'collector_manager']
