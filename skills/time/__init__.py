"""
time 技能模块
"""

from .time_skill import FormatDateSkill


def execute(params=None):
    """统一执行入口"""
    skill = FormatDateSkill()
    return skill.execute(params)
