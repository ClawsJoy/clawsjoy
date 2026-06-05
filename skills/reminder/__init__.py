"""
reminder 技能模块
"""

from .reminder_skill import SetReminderSkill


def execute(params=None):
    """统一执行入口"""
    skill = SetReminderSkill()
    return skill.execute(params)
