"""
voice_script_writer 技能模块
"""

from .voice_script_writer_skill import VoiceScriptWriter


def execute(params=None):
    """统一执行入口"""
    skill = VoiceScriptWriter()
    return skill.execute(params)
