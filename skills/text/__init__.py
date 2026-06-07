\"\"\"text 技能\"\"\"

from .text_skill import text


def execute(params):
    skill = text()
    return skill.execute(params)
