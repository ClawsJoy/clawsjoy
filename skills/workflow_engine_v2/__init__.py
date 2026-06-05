"""
workflow_engine_v2 技能模块
"""

from .workflow_engine_v2_skill import WorkflowEngineV2


def execute(params=None):
    """统一执行入口"""
    skill = WorkflowEngineV2()
    return skill.execute(params)
