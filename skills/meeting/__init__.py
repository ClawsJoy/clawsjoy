"""
meeting 技能模块
"""

from .meeting_skill import BookRoomSkill


def execute(params=None):
    """统一执行入口"""
    skill = BookRoomSkill()
    return skill.execute(params)
