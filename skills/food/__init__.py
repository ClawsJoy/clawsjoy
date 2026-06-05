"""
food 技能模块
"""

from .food_skill import RecipeSkill


def execute(params=None):
    """统一执行入口"""
    skill = RecipeSkill()
    return skill.execute(params)
