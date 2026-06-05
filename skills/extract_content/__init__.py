"""
extract_content 技能模块
"""

from .extract_content_skill import ExtractContentSkill


def execute(params=None):
    skill = ExtractContentSkill()
    return skill.execute(params)
