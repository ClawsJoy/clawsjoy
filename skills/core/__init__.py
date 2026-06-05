"""
core 技能模块
"""

from .core_skill import ToStringSkill


def execute(params=None):
    """统一执行入口"""
    skill = ToStringSkill()
    return skill.execute(params)
