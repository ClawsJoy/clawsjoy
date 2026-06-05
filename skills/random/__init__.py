"""
random 技能模块
"""

from .random_skill import RandomChoiceSkill


def execute(params=None):
    """统一执行入口"""
    skill = RandomChoiceSkill()
    return skill.execute(params)
