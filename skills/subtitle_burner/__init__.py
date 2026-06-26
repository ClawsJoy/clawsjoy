"""subtitle_burner 技能"""

from .subtitle_burner_skill import subtitle_burner


def execute(params=None):
    if params is None:
        params = {}
    return subtitle_burner().execute(params)
