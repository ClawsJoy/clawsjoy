\"\"\"video-public 技能\"\"\"

from .video-public_skill import video_public


def execute(params):
    skill = video_public()
    return skill.execute(params)
