"""
series_manager 技能模块
"""

from .series_manager_skill import SeriesManager


def execute(params=None):
    """统一执行入口"""
    skill = SeriesManager()
    return skill.execute(params)
