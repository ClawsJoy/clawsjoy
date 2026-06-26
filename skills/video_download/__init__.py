"""video_download 技能"""

from .video_download_skill import video_download


def execute(params=None):
    if params is None:
        params = {}
    return video_download().execute(params)
