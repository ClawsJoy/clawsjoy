\"\"\"atomic 技能\"\"\"

from .atomic_skill import atomic


def execute(params):
    skill = atomic()
    return skill.execute(params)
