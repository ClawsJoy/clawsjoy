\"\"\"check-video-status 技能\"\"\"

from .check-video-status_skill import check_video_status


def execute(params):
    skill = check_video_status()
    return skill.execute(params)
