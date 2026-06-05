"""
url_discovery 技能模块
"""

from .url_discovery_skill import UrlDiscovery


def execute(params=None):
    """统一执行入口"""
    skill = UrlDiscovery()
    return skill.execute(params)
