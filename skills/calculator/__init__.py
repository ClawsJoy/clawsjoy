"""
calculator 技能模块
"""

from .calculator_skill import CalculatorSkill


def execute(params=None):
    """统一执行入口"""
    skill = CalculatorSkill()
    return skill.execute(params)
