"""
extract_content_v2 技能模块
"""

from .extract_content_v2_skill import ExtractContentV2Skill


def execute(params=None):
    """统一执行入口"""
    skill = ExtractContentV2Skill()
    return skill.execute(params)
