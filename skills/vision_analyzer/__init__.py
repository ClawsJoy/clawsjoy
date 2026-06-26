"""vision_analyzer 技能"""

from .vision_analyzer_skill import vision_analyzer


def execute(params=None):
    if params is None:
        params = {}
    return vision_analyzer().execute(params)
