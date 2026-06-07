\"\"\"text-to-image 技能\"\"\"

from .text-to-image_skill import text_to_image


def execute(params):
    skill = text_to_image()
    return skill.execute(params)
