"""
workflow_engine 技能模块
"""

from .workflow_engine_skill import WorkflowEngine


def execute(params=None):
    """统一执行入口"""
    skill = WorkflowEngine()
    return skill.execute(params)
