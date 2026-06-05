"""
self_heal 技能模块
"""

from .self_heal_skill import SelfHeal


def execute(params=None):
    """统一执行入口"""
    skill = SelfHeal()
    return skill.execute(params)
