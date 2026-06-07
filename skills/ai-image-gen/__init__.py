\"\"\"ai-image-gen 技能\"\"\"

from .ai-image-gen_skill import ai_image_gen


def execute(params):
    skill = ai_image_gen()
    return skill.execute(params)
