"""video_understand 技能"""

from .video_understand_skill import VideoUnderstandSkill


def execute(params=None):
    if params is None:
        params = {}
    return VideoUnderstandSkill().execute(params)
