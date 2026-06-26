"""gpu_safe 技能"""

from .gpu_safe_skill import gpu_safe_skill


def execute(params=None):
    if params is None:
        params = {}
    return gpu_safe_skill().execute(params)
