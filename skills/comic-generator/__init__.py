\"\"\"comic-generator 技能\"\"\"

from .comic-generator_skill import comic_generator


def execute(params):
    skill = comic_generator()
    return skill.execute(params)
