"""
travel 技能模块
"""

from .travel_skill import NavigationSkill


def execute(params=None):
    """统一执行入口"""
    skill = NavigationSkill()
    return skill.execute(params)
