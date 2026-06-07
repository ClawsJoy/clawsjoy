\"\"\"simple-script 技能\"\"\"

from .simple-script_skill import simple_script


def execute(params):
    skill = simple_script()
    return skill.execute(params)
