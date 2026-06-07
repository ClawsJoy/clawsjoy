\"\"\"three-d 技能\"\"\"

from .three-d_skill import three_d


def execute(params):
    skill = three_d()
    return skill.execute(params)
