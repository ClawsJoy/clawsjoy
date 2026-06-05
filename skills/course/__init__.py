"""
course 技能模块
"""

from .course_skill import LearnEnglishSkill


def execute(params=None):
    """统一执行入口"""
    skill = LearnEnglishSkill()
    return skill.execute(params)
