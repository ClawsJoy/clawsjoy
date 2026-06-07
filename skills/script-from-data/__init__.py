\"\"\"script-from-data 技能\"\"\"

from .script-from-data_skill import script_from_data


def execute(params):
    skill = script_from_data()
    return skill.execute(params)
