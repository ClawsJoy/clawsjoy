"""
text_basic 技能模块
"""

from .text_basic_skill import SplitTextSkill


def execute(params=None):
    """统一执行入口"""
    skill = SplitTextSkill()
    return skill.execute(params)
