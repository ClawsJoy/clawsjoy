"""
sales 技能模块
"""

from .sales_skill import UpdatePipelineSkill


def execute(params=None):
    """统一执行入口"""
    skill = UpdatePipelineSkill()
    return skill.execute(params)
