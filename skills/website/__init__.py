"""
website 技能模块
"""

from .website_skill import BackupWebsiteSkill


def execute(params=None):
    """统一执行入口"""
    skill = BackupWebsiteSkill()
    return skill.execute(params)
