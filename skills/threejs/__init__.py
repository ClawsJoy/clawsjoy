"""
threejs 技能模块
"""

from .threejs_skill import ThreeJSSkill


def execute(params=None):
    """统一执行入口"""
    skill = ThreeJSSkill()
    return skill.execute(params)
