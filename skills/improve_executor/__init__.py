"""
improve_executor 技能模块
"""

from .improve_executor_skill import ImproveExecutor


def execute(params=None):
    """统一执行入口"""
    skill = ImproveExecutor()
    return skill.execute(params)
