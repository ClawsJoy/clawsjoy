"""
study_plan 技能模块
"""

from .study_plan_skill import CreateStudyPlanSkill


def execute(params=None):
    """统一执行入口"""
    skill = CreateStudyPlanSkill()
    return skill.execute(params)
