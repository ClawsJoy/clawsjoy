"""
news 技能模块
"""

from .news_skill import GetNewsSkill


def execute(params=None):
    """统一执行入口"""
    skill = GetNewsSkill()
    return skill.execute(params)
