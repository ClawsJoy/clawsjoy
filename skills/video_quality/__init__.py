"""video_quality 技能"""

from .video_quality_skill import VideoQualitySkill


def execute(params=None):
    if params is None:
        params = {}
    return VideoQualitySkill().execute(params)
