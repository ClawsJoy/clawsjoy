\"\"\"email 技能\"\"\"

from .email_skill import email


def execute(params):
    skill = email()
    return skill.execute(params)
