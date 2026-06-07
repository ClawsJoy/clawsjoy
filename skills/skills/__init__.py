\"\"\"skills 技能\"\"\"

from .skills_skill import skills


def execute(params):
    skill = skills()
    return skill.execute(params)
