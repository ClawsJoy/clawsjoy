\"\"\"self-heal 技能\"\"\"

from .self-heal_skill import self_heal


def execute(params):
    skill = self_heal()
    return skill.execute(params)
