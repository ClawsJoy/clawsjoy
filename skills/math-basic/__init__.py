\"\"\"math-basic 技能\"\"\"

from .math-basic_skill import math_basic


def execute(params):
    skill = math_basic()
    return skill.execute(params)
