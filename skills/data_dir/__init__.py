"""data 技能"""

from .data_skill import data


def execute(params=None):
    if params is None:
        params = {}
    return data().execute(params)
