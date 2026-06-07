\"\"\"math 技能\"\"\"

from .math_skill import math


def execute(params):
    skill = math()
    return skill.execute(params)
