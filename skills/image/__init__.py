"""
image 技能模块
"""

from .image_skill import VisionSkill


def execute(params=None):
    """统一执行入口"""
    skill = VisionSkill()
    return skill.execute(params)
