"""
pro_script_3min 技能模块
"""

from .pro_script_3min_skill import ProScript3min


def execute(params=None):
    """统一执行入口"""
    skill = ProScript3min()
    return skill.execute(params)
