\"\"\"image 技能\"\"\"

from .image_skill import image


def execute(params):
    skill = image()
    return skill.execute(params)
