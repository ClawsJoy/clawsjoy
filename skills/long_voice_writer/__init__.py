"""
long_voice_writer 技能模块
"""

from .long_voice_writer_skill import LongVoiceWriterSkill


def execute(params=None):
    """统一执行入口"""
    skill = LongVoiceWriterSkill()
    return skill.execute(params)
