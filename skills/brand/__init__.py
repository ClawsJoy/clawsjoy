"""
brand 技能模块
"""

from .brand_skill import MonitorMentionSkill


def execute(params=None):
    """统一执行入口"""
    skill = MonitorMentionSkill()
    return skill.execute(params)
