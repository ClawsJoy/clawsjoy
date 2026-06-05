"""
scheduler 技能模块
"""

from .scheduler_skill import Scheduler


def execute(params=None):
    """统一执行入口"""
    skill = Scheduler()
    return skill.execute(params)
