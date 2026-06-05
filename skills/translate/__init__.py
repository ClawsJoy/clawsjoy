"""
translate 技能模块
"""

from .translate_skill import TranslateSkill


def execute(params=None):
    """统一执行入口"""
    skill = TranslateSkill()
    return skill.execute(params)
