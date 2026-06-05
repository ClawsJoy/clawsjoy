"""
text 技能模块
"""

from .text_skill import ToUpperSkill


def execute(params=None):
    """统一执行入口"""
    skill = ToUpperSkill()
    return skill.execute(params)
