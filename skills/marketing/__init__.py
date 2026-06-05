"""
marketing 技能模块
"""

from .marketing_skill import AnalyzeTrendSkill


def execute(params=None):
    """统一执行入口"""
    skill = AnalyzeTrendSkill()
    return skill.execute(params)
