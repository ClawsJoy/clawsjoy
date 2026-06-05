"""
memory 技能模块
"""

from .memory_skill import Memory


def execute(params=None):
    """统一执行入口"""
    skill = Memory()
    return skill.execute(params)
