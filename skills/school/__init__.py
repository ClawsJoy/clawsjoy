"""
school 技能模块
"""

from .school_skill import CheckHomeworkSkill


def execute(params=None):
    """统一执行入口"""
    skill = CheckHomeworkSkill()
    return skill.execute(params)
