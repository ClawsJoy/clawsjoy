"""
ai 技能模块
"""

from .ai_skill import AIAgent


def execute(params=None):
    """统一执行入口"""
    skill = AIAgent()
    return skill.execute(params)
