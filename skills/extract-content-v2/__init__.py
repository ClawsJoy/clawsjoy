\"\"\"extract-content-v2 技能\"\"\"

from .extract-content-v2_skill import extract_content_v2


def execute(params):
    skill = extract_content_v2()
    return skill.execute(params)
