\"\"\"threejs 技能\"\"\"

from .threejs_skill import threejs


def execute(params):
    skill = threejs()
    return skill.execute(params)
