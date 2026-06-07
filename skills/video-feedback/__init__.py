\"\"\"video-feedback 技能\"\"\"

from .video-feedback_skill import Skill


def execute(params):
    s = Skill()
    return s.execute(params)
