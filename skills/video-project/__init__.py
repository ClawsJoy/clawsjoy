\"\"\"video-project 技能\"\"\"

from .video-project_skill import video_project


def execute(params):
    skill = video_project()
    return skill.execute(params)
