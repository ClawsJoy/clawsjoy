\"\"\"video-understand 技能\"\"\"

from .video-understand_skill import Skill


def execute(params):
    s = Skill()
    return s.execute(params)
