"""
gpu_safe 技能模块
"""

from .gpu_safe_skill import GPUSafeRenderSkill


def execute(params=None):
    """统一执行入口"""
    skill = GPUSafeRenderSkill()
    return skill.execute(params)
