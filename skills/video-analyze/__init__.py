\"\"\"video-analyze 技能\"\"\"

from .video-analyze_skill import video_analyze


def execute(params):
    skill = video_analyze()
    return skill.execute(params)
