"""video_scene 技能"""

from .video_scene_skill import VideoSceneSkill


def execute(params=None):
    if params is None:
        params = {}
    return VideoSceneSkill().execute(params)
