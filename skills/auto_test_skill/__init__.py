"""
auto_test_skill 技能模块
"""

from .auto_test_skill_skill import AutoTestSkill


def execute(params=None):
    """统一执行入口"""
    skill = AutoTestSkill()
    return skill.execute(params)
