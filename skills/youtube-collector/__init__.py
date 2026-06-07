\"\"\"youtube-collector 技能\"\"\"

from .youtube-collector_skill import youtube_collector


def execute(params):
    skill = youtube_collector()
    return skill.execute(params)
