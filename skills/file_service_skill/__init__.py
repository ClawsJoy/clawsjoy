"""
file_service_skill 技能模块
"""

from .file_service_skill_skill import FileServiceSkill


def execute(params=None):
    """统一执行入口"""
    skill = FileServiceSkill()
    return skill.execute(params)
