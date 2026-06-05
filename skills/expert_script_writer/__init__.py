"""
expert_script_writer 技能模块
"""

from .expert_script_writer_skill import ExpertScriptWriterSkill


def execute(params=None):
    skill = ExpertScriptWriterSkill()
    return skill.execute(params)
