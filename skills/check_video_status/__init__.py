"""
check_video_status 技能模块
"""

from .check_video_status_skill import CheckVideoStatus


def execute(params=None):
    """统一执行入口"""
    skill = CheckVideoStatus()
    return skill.execute(params)
