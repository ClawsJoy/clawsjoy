"""
script_from_data 技能模块
"""

from .script_from_data_skill import ScriptFromDataSkill


def execute(params=None):
    """统一执行入口"""
    skill = ScriptFromDataSkill()
    return skill.execute(params)
