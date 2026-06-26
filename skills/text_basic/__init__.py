"""text_basic 技能"""

from .text_basic_skill import text_basic


def execute(params=None):
    if params is None:
        params = {}
    return text_basic().execute(params)
