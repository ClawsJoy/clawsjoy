"""
math_basic 技能模块
"""

from .math_basic_skill import PercentageSkill


def execute(params=None):
    """统一执行入口"""
    skill = PercentageSkill()
    return skill.execute(params)
