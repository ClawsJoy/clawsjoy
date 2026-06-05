"""
system 技能模块
"""

from .system_skill import EnvVarSkill


def execute(params=None):
    """统一执行入口"""
    skill = EnvVarSkill()
    return skill.execute(params)
