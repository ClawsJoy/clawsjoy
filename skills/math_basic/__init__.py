"""math_basic 技能"""

from .math_basic_skill import math_basic


def execute(params=None):
    if params is None:
        params = {}
    return math_basic().execute(params)
