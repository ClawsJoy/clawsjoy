"""
childcare 技能模块
"""

from .childcare_skill import TemperatureSkill


def execute(params=None):
    """统一执行入口"""
    skill = TemperatureSkill()
    return skill.execute(params)
