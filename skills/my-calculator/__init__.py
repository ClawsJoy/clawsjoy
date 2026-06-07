\"\"\"my-calculator 技能\"\"\"

from .my-calculator_skill import my_calculator


def execute(params):
    skill = my_calculator()
    return skill.execute(params)
