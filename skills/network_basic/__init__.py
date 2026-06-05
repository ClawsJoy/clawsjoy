"""
network_basic 技能模块
"""

from .network_basic_skill import HttpGetSkill


def execute(params=None):
    """统一执行入口"""
    skill = HttpGetSkill()
    return skill.execute(params)
