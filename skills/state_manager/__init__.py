"""
state_manager 技能模块
"""

from .state_manager_skill import StateManager


def execute(params=None):
    """统一执行入口"""
    skill = StateManager()
    return skill.execute(params)
