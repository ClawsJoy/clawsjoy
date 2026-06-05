"""
my_calculator 技能模块
"""

from .my_calculator_skill import MyCalculator


def execute(params=None):
    """统一执行入口"""
    skill = MyCalculator()
    return skill.execute(params)
