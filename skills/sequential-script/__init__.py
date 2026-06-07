\"\"\"sequential-script 技能\"\"\"

from .sequential-script_skill import sequential_script


def execute(params):
    skill = sequential_script()
    return skill.execute(params)
