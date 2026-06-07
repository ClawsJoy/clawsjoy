\"\"\"data-merger 技能\"\"\"

from .data-merger_skill import data_merger


def execute(params):
    skill = data_merger()
    return skill.execute(params)
