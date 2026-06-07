\"\"\"doc 技能\"\"\"

from .doc_skill import doc


def execute(params):
    skill = doc()
    return skill.execute(params)
