"""
memory_integration 技能模块
"""

from .memory_integration_skill import MemoryIntegration


def execute(params=None):
    """统一执行入口"""
    skill = MemoryIntegration()
    return skill.execute(params)
