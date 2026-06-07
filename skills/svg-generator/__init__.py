\"\"\"svg-generator 技能\"\"\"

from .svg-generator_skill import svg_generator


def execute(params):
    skill = svg_generator()
    return skill.execute(params)
