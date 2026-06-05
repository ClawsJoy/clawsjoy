"""
schedule 技能模块
"""

from .schedule_skill import ListEventsSkill


def execute(params=None):
    """统一执行入口"""
    skill = ListEventsSkill()
    return skill.execute(params)
