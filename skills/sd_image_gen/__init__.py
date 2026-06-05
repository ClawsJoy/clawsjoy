"""
sd_image_gen 技能模块
"""

from .sd_image_gen_skill import SdImageGen


def execute(params=None):
    """统一执行入口"""
    skill = SdImageGen()
    return skill.execute(params)
