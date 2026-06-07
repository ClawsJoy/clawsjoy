\"\"\"sd-image-gen 技能\"\"\"

from .sd-image-gen_skill import sd_image_gen


def execute(params):
    skill = sd_image_gen()
    return skill.execute(params)
