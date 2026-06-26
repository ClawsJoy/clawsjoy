"""weather 技能"""

from .weather_skill import weather_skill


def execute(params=None):
    if params is None:
        params = {}
    return weather_skill().execute(params)
