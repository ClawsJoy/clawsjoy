"""
shopping 技能模块
"""

from .shopping_skill import ProductSearchSkill


def execute(params=None):
    """统一执行入口"""
    skill = ProductSearchSkill()
    return skill.execute(params)
