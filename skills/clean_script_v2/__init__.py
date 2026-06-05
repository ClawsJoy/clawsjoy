"""
脚本清理 V2 技能模块
"""

from .clean_script_v2_skill import CleanScriptV2Skill


def execute(params=None):
    skill = CleanScriptV2Skill()
    return skill.execute(params)
