"""
AI 图像生成技能模块
"""

from .ai_image_gen_skill import AIImageGenSkill


def execute(params=None):
    skill = AIImageGenSkill()
    return skill.execute(params)
