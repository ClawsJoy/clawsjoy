"""
doc 技能模块
"""

from .doc_skill import Doc


def execute(params=None):
    """统一执行入口"""
    skill = Doc()
    return skill.execute(params)
