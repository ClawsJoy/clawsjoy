\"\"\"social 技能\"\"\"

from .social_skill import social


def execute(params):
    skill = social()
    return skill.execute(params)
