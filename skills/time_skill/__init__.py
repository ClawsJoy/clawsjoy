"""time 技能"""

from .time_skill import time_skill


def execute(params=None):
    if params is None:
        params = {}
    return time_skill().execute(params)
