"""
tools 技能模块
"""

from .tools_skill import ToolsSkill


def execute(params=None):
    """统一执行入口"""
    skill = ToolsSkill()
    return skill.execute(params)
