\"\"\"improve-executor 技能\"\"\"

from .improve-executor_skill import improve_executor


def execute(params):
    skill = improve_executor()
    return skill.execute(params)
