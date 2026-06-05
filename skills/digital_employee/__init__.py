"""
digital_employee 技能模块
"""

from .digital_employee_skill import ProcessInvoiceSkill


def execute(params=None):
    """统一执行入口"""
    skill = ProcessInvoiceSkill()
    return skill.execute(params)
