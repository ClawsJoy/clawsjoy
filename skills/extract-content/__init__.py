\"\"\"extract-content 技能\"\"\"

from .extract-content_skill import extract_content


def execute(params):
    skill = extract_content()
    return skill.execute(params)
