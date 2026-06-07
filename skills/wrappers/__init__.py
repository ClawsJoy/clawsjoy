\"\"\"wrappers 技能\"\"\"

from .wrappers_skill import wrappers


def execute(params):
    skill = wrappers()
    return skill.execute(params)
