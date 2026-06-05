"""
email 技能模块
"""

from .email_skill import SendEmailSkill


def execute(params=None):
    """统一执行入口"""
    skill = SendEmailSkill()
    return skill.execute(params)
