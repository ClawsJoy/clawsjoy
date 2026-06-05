"""
content_writer 技能模块
"""

from .content_writer_skill import ContentWriterSkill


def execute(params=None):
    skill = ContentWriterSkill()
    return skill.execute(params)
