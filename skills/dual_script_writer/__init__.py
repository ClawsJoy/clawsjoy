"""
dual_script_writer 技能模块
"""

from .dual_script_writer_skill import DualScriptWriterSkill


def execute(params=None):
    skill = DualScriptWriterSkill()
    return skill.execute(params)
