"""
data_merger 技能模块
"""

from .data_merger_skill import DataMergerSkill


def execute(params=None):
    skill = DataMergerSkill()
    return skill.execute(params)
