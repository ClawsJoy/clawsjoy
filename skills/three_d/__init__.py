"""
three_d 技能模块
"""

from .three_d_skill import Blender3DSkill


def execute(params=None):
    """统一执行入口"""
    skill = Blender3DSkill()
    return skill.execute(params)
