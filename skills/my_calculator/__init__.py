"""my_calculator 技能"""

from .my_calculator_skill import my_calculator


def execute(params=None):
    if params is None:
        params = {}
    return my_calculator().execute(params)
