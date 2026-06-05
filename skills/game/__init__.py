"""
game 技能模块
"""

from .game_skill import QuizGameSkill


def execute(params=None):
    """统一执行入口"""
    skill = QuizGameSkill()
    return skill.execute(params)
