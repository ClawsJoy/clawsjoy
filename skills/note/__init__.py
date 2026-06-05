"""
note 技能模块
"""

from .note_skill import AddNoteSkill


def execute(params=None):
    """统一执行入口"""
    skill = AddNoteSkill()
    return skill.execute(params)
