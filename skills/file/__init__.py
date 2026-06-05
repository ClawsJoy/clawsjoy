"""
file 技能模块
"""

from .file_skill import ReadFileSkill


def execute(params=None):
    """统一执行入口"""
    skill = ReadFileSkill()
    return skill.execute(params)
