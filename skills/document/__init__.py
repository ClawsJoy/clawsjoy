"""
document 技能模块
"""

from .document_skill import CreateDocSkill


def execute(params=None):
    """统一执行入口"""
    skill = CreateDocSkill()
    return skill.execute(params)
