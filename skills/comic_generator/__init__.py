"""
comic_generator 技能模块
"""

from .comic_generator_skill import ComicGeneratorSkill


def execute(params=None):
    skill = ComicGeneratorSkill()
    return skill.execute(params)
