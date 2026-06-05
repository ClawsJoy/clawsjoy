"""
Webhook通知
"""


class WebhookNotify:
    name = "webhook_notify"
    description = "Webhook通知"
    version = "2.0.0"

    def execute(self, params=None):
        """执行技能"""
        # TODO: 实现具体功能
        return {
            "success": True,
            "result": f"Webhook通知 执行成功",
            "data": params or {},
        }
