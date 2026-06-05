"""
vision 技能模块
"""

from .vision_skill import VisionSkill


def execute(params=None):
    """统一执行入口"""
    skill = VisionSkill()
    return skill.execute(params)
