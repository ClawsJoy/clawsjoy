"""
home 技能模块
"""

from .home_skill import LightSkill


def execute(params=None):
    """统一执行入口"""
    skill = LightSkill()
    return skill.execute(params)
