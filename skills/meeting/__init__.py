\"\"\"meeting 技能\"\"\"

from .meeting_skill import meeting


def execute(params):
    skill = meeting()
    return skill.execute(params)
