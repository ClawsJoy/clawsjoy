\"\"\"clean-script 技能\"\"\"

from .clean-script_skill import clean_script


def execute(params):
    skill = clean_script()
    return skill.execute(params)
