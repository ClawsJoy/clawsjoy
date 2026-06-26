"""network 技能"""

from .network_skill import network_skill


def execute(params=None):
    if params is None:
        params = {}
    return network_skill().execute(params)
