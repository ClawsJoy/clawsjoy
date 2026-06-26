"""version 技能"""

from .version_skill import version_skill


def execute(params=None):
    if params is None:
        params = {}
    return version_skill().execute(params)
