"""
svg 技能模块
"""

from .svg_skill import SVGGenerator


def execute(params=None):
    """统一执行入口"""
    skill = SVGGenerator()
    return skill.execute(params)
