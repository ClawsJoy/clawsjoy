"""
long_script_gen 技能模块
"""

from .long_script_gen_skill import LongScriptGenSkill


def execute(params=None):
    """统一执行入口"""
    skill = LongScriptGenSkill()
    return skill.execute(params)
