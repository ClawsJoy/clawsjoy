"""
ops_skills 技能模块
"""

from .ops_skills_skill import OpsSkills


def execute(params=None):
    """统一执行入口"""
    skill = OpsSkills()
    return skill.execute(params)
