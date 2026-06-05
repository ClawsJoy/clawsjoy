"""
webhook_notify 技能模块
"""

from .webhook_notify_skill import WebhookNotify


def execute(params=None):
    """统一执行入口"""
    skill = WebhookNotify()
    return skill.execute(params)
