"""cinematic_render 技能"""

from .cinematic_render_skill import cinematic_render


def execute(params=None):
    if params is None:
        params = {}
    return cinematic_render().execute(params)
