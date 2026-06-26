"""atomic 技能"""

from .atomic_skill import atomic


def execute(params=None):
    if params is None:
        params = {}
    return atomic().execute(params)
