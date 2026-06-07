\"\"\"file 技能\"\"\"

from .file_skill import file


def execute(params):
    skill = file()
    return skill.execute(params)
