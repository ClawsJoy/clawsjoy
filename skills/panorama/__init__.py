"""
panorama 技能模块
"""

from .panorama_skill import PanoramaSkill


def execute(params=None):
    """统一执行入口"""
    skill = PanoramaSkill()
    return skill.execute(params)
