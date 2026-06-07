\"\"\"convert 技能\"\"\"

from .convert_skill import convert


def execute(params):
    skill = convert()
    return skill.execute(params)
