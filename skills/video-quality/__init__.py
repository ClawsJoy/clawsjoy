\"\"\"video-quality 技能\"\"\"

from .video-quality_skill import Skill


def execute(params):
    s = Skill()
    return s.execute(params)
