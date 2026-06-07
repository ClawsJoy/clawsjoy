\"\"\"clean-script-v2 技能\"\"\"

from .clean-script-v2_skill import clean_script_v2


def execute(params):
    skill = clean_script_v2()
    return skill.execute(params)
