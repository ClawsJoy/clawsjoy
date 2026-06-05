"""
image_scheduler 技能模块
"""

from .image_scheduler_skill import ImageSchedulerSkill


def execute(params=None):
    """统一执行入口"""
    skill = ImageSchedulerSkill()
    return skill.execute(params)
