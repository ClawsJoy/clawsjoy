\"\"\"cartoon-images 技能\"\"\"

from .cartoon-images_skill import cartoon_images


def execute(params):
    skill = cartoon_images()
    return skill.execute(params)
