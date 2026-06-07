\"\"\"document 技能\"\"\"

from .document_skill import document


def execute(params):
    skill = document()
    return skill.execute(params)
