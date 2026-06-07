\"\"\"scripts 技能\"\"\"

from .scripts_skill import scripts


def execute(params):
    skill = scripts()
    return skill.execute(params)
