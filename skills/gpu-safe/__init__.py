\"\"\"gpu-safe 技能\"\"\"

from .gpu-safe_skill import gpu_safe


def execute(params):
    skill = gpu_safe()
    return skill.execute(params)
