\"\"\"content-writer 技能\"\"\"

from .content-writer_skill import content_writer


def execute(params):
    skill = content_writer()
    return skill.execute(params)
