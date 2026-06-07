\"\"\"version 技能\"\"\"

from .version_skill import version


def execute(params):
    skill = version()
    return skill.execute(params)
