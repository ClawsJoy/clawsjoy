"""
math 技能模块
"""

from .math_skill import DivideSkill


def execute(params=None):
    """统一执行入口"""
    skill = DivideSkill()
    return skill.execute(params)
