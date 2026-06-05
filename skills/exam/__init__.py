"""
exam 技能模块
"""

from .exam_skill import MockTestSkill


def execute(params=None):
    """统一执行入口"""
    skill = MockTestSkill()
    return skill.execute(params)
