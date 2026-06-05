"""
security 技能模块
"""

from .security_skill import GenPasswordSkill


def execute(params=None):
    """统一执行入口"""
    skill = GenPasswordSkill()
    return skill.execute(params)
