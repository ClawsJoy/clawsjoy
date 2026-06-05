"""
sports 技能模块
"""

from .sports_skill import StepCounterSkill


def execute(params=None):
    """统一执行入口"""
    skill = StepCounterSkill()
    return skill.execute(params)
