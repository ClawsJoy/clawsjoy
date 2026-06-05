"""
video_description 技能模块
"""

from .video_description_skill import VideoDescription


def execute(params=None):
    """统一执行入口"""
    skill = VideoDescription()
    return skill.execute(params)
