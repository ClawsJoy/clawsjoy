"""
audio 技能模块
"""

from .audio_skill import TTSSkill


def execute(params=None):
    """统一执行入口"""
    skill = TTSSkill()
    return skill.execute(params)
