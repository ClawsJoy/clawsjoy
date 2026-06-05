"""
safety 技能模块
"""

from .safety_skill import GasSensorSkill


def execute(params=None):
    """统一执行入口"""
    skill = GasSensorSkill()
    return skill.execute(params)
