"""
atomic 技能模块
"""

from .atomic_skill import Atomic


def execute(params=None):
    """统一执行入口"""
    skill = Atomic()
    return skill.execute(params)
