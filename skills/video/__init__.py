"""
video 技能模块
"""

from .video_skill import VideoSkill


def execute(params=None):
    """统一执行入口"""
    skill = VideoSkill()
    return skill.execute(params)
