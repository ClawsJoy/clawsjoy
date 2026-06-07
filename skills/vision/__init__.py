\"\"\"vision 技能\"\"\"

from .vision_skill import vision


def execute(params):
    skill = vision()
    return skill.execute(params)
