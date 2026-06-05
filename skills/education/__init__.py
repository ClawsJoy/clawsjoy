"""
education 技能模块
"""

from .education_skill import DrawingSkill


def execute(params=None):
    """统一执行入口"""
    skill = DrawingSkill()
    return skill.execute(params)
