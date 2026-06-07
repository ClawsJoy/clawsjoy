\"\"\"text-basic 技能\"\"\"

from .text-basic_skill import text_basic


def execute(params):
    skill = text_basic()
    return skill.execute(params)
