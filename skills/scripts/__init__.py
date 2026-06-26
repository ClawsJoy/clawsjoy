"""scripts 技能"""

from .scripts_skill import scripts


def execute(params=None):
    if params is None:
        params = {}
    return scripts().execute(params)
