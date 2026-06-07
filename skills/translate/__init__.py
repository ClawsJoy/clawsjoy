\"\"\"translate 技能\"\"\"

from .translate_skill import translate


def execute(params):
    skill = translate()
    return skill.execute(params)
