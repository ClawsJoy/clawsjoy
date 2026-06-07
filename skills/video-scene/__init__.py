\"\"\"video-scene 技能\"\"\"

from .video-scene_skill import Skill


def execute(params):
    s = Skill()
    return s.execute(params)
