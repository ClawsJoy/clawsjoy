"""
social 技能模块
"""

from .social_skill import GroupNotifySkill


def execute(params=None):
    """统一执行入口"""
    skill = GroupNotifySkill()
    return skill.execute(params)
