"""
clean_script 技能模块
"""

from .clean_script_skill import CleanScriptSkill


def execute(params=None):
    skill = CleanScriptSkill()
    return skill.execute(params)
