"""
entertainment 技能模块
"""

from .entertainment_skill import PlayMusicSkill


def execute(params=None):
    """统一执行入口"""
    skill = PlayMusicSkill()
    return skill.execute(params)
