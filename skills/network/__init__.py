"""
network 技能模块
"""

from .network_skill import Network


def execute(params=None):
    """统一执行入口"""
    skill = Network()
    return skill.execute(params)
