"""
opengl 技能模块
"""

from .opengl_skill import OpenGLRenderSkill


def execute(params=None):
    """统一执行入口"""
    skill = OpenGLRenderSkill()
    return skill.execute(params)
