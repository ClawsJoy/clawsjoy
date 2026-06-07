\"\"\"storyteller 技能\"\"\"

from .storyteller_skill import storyteller


def execute(params):
    skill = storyteller()
    return skill.execute(params)
