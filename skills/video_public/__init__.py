"""video_public 技能"""

from .video_public_skill import video_public


def execute(params=None):
    if params is None:
        params = {}
    return video_public().execute(params)
