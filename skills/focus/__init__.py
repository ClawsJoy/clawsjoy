"""
focus 技能模块
"""

from .focus_skill import PomodoroSkill


def execute(params=None):
    """统一执行入口"""
    skill = PomodoroSkill()
    return skill.execute(params)
