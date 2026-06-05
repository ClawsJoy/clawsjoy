"""
finance 技能模块
"""

from .finance_skill import FundSearchSkill


def execute(params=None):
    """统一执行入口"""
    skill = FundSearchSkill()
    return skill.execute(params)
