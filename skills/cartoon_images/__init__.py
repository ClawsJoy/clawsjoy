"""
cartoon_images 技能模块
"""

from .cartoon_images_skill import CartoonImagesSkill


def execute(params=None):
    skill = CartoonImagesSkill()
    return skill.execute(params)
