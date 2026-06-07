\"\"\"video-trim 技能\"\"\"

from .video-trim_skill import video_trim


def execute(params):
    skill = video_trim()
    return skill.execute(params)
