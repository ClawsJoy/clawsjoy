"""svg_generator 技能"""

from .svg_generator_skill import svg_generator


def execute(params=None):
    if params is None:
        params = {}
    return svg_generator().execute(params)
