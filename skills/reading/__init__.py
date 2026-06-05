"""
reading 技能模块
"""

from .reading_skill import GetSummarySkill


def execute(params=None):
    """统一执行入口"""
    skill = GetSummarySkill()
    return skill.execute(params)
