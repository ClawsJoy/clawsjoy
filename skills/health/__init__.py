"""
health 技能模块
"""

from .health_skill import MedicationReminderSkill


def execute(params=None):
    """统一执行入口"""
    skill = MedicationReminderSkill()
    return skill.execute(params)
