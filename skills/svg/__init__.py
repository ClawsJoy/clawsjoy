\"\"\"svg 技能\"\"\"

from .svg_skill import svg


def execute(params):
    skill = svg()
    return skill.execute(params)
