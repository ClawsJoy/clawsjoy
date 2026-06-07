\"\"\"cinematic-render 技能\"\"\"

from .cinematic-render_skill import cinematic_render


def execute(params):
    skill = cinematic_render()
    return skill.execute(params)
