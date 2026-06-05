"""
svg_generator 技能模块
"""

from .svg_generator_skill import SvgGenerator


def execute(params=None):
    """统一执行入口"""
    skill = SvgGenerator()
    return skill.execute(params)
