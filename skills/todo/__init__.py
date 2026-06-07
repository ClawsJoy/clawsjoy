\"\"\"todo 技能\"\"\"

from .todo_skill import todo


def execute(params):
    skill = todo()
    return skill.execute(params)
