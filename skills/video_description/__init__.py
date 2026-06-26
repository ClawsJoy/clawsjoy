"""video_description 技能"""

from .video_description_skill import VideoDescription


def execute(params=None):
    if params is None:
        params = {}
    return VideoDescription().execute(params)
