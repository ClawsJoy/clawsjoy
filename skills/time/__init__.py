\"\"\"time 技能\"\"\"

from .time_skill import time


def execute(params):
    skill = time()
    return skill.execute(params)
