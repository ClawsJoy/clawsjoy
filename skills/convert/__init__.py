"""
convert 技能模块
"""

from .convert_skill import UnitConvertSkill


def execute(params=None):
    """统一执行入口"""
    skill = UnitConvertSkill()
    return skill.execute(params)
