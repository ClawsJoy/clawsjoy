\"\"\"video-understanding 技能\"\"\"

from .video-understanding_skill import video_understanding


def execute(params):
    skill = video_understanding()
    return skill.execute(params)
