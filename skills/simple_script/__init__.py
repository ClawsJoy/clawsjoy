"""
simple_script 技能模块
"""

from .simple_script_skill import SimpleScript


def execute(params=None):
    """统一执行入口"""
    skill = SimpleScript()
    return skill.execute(params)
