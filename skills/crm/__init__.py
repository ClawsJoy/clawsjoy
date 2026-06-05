"""
crm 技能模块
"""

from .crm_skill import AddCustomerSkill


def execute(params=None):
    """统一执行入口"""
    skill = AddCustomerSkill()
    return skill.execute(params)
