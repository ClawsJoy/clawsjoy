"""subtitle-burner 技能"""
from .subtitle_burner_skill import subtitle_burner

def execute(params):
    skill = subtitle_burner()
    return skill.execute(params)
