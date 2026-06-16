"""video-download 技能"""

from .video_download_skill import video_download

def execute(params):
    skill = video_download()
    return skill.execute(params)
