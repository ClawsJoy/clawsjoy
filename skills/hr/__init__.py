"""
hr 技能模块
"""

from .hr_skill import OnboardingSkill


def execute(params=None):
    """统一执行入口"""
    skill = OnboardingSkill()
    return skill.execute(params)
