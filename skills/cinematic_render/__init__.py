"""
cinematic_render 技能模块
"""

from .cinematic_render_skill import CinematicRenderSkill


def execute(params=None):
    """统一执行入口"""
    skill = CinematicRenderSkill()
    return skill.execute(params)
