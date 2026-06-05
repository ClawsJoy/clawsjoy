"""YouTube 数据采集技能"""

from .youtube_collector_skill import YouTubeCollectorSkill

def execute(params):
    skill = YouTubeCollectorSkill()
    return skill.execute(params)
