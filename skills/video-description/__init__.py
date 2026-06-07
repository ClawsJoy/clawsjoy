\"\"\"video-description 技能\"\"\"

from .video-description_skill import video_description


def execute(params):
    skill = video_description()
    return skill.execute(params)
