"""
extracurricular 技能模块
"""

from .extracurricular_skill import LearnCodingSkill


def execute(params=None):
    """统一执行入口"""
    skill = LearnCodingSkill()
    return skill.execute(params)
