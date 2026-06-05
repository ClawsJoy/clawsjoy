"""
pro_script_writer 技能模块
"""

from .pro_script_writer_skill import ProScriptWriter


def execute(params=None):
    """统一执行入口"""
    skill = ProScriptWriter()
    return skill.execute(params)
