\"\"\"calculator 技能\"\"\"

from .calculator_skill import calculator


def execute(params):
    skill = calculator()
    return skill.execute(params)
