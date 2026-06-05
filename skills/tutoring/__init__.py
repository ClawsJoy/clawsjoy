"""
tutoring 技能模块
"""

from .tutoring_skill import ExplainProblemSkill


def execute(params=None):
    """统一执行入口"""
    skill = ExplainProblemSkill()
    return skill.execute(params)
