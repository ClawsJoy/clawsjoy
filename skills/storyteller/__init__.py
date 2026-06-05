"""
storyteller 技能模块
"""

from .storyteller_skill import Storyteller


def execute(params=None):
    """统一执行入口"""
    skill = Storyteller()
    return skill.execute(params)
