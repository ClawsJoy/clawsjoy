\"\"\"memory 技能\"\"\"

from .memory_skill import memory


def execute(params):
    skill = memory()
    return skill.execute(params)
