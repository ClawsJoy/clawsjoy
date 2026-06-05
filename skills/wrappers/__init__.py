"""
wrappers 技能模块
"""

from .wrappers_skill import Wrappers


def execute(params=None):
    """统一执行入口"""
    skill = Wrappers()
    return skill.execute(params)
