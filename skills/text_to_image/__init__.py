"""
text_to_image 技能模块
"""

from .text_to_image_skill import TextToImageSkill


def execute(params=None):
    """统一执行入口"""
    skill = TextToImageSkill()
    return skill.execute(params)
