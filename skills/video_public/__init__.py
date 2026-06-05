"""
video_public 技能模块
"""

from .video_public_skill import VideoPublic


def execute(params=None):
    """统一执行入口"""
    skill = VideoPublic()
    return skill.execute(params)
