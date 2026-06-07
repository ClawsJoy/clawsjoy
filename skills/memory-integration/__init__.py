\"\"\"memory-integration 技能\"\"\"

from .memory-integration_skill import memory_integration


def execute(params):
    skill = memory_integration()
    return skill.execute(params)
