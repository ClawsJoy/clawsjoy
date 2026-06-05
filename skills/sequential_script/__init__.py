"""
sequential_script 技能模块
"""

from .sequential_script_skill import SequentialScript


def execute(params=None):
    """统一执行入口"""
    skill = SequentialScript()
    return skill.execute(params)
