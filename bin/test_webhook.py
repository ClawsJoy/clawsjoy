#!/usr/bin/env python3
"""测试 Webhook 通知"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy/bin")
from webhook_notify import WebhookNotify


def test():
    print("=== Webhook 通知测试 ===\n")

    notify = WebhookNotify()

    # 测试 Workflow 通知
    print("1. 测试 Workflow 完成通知")
    notify.notify_workflow("test_workflow_001", "completed", {"success": True})

    print("\n2. 测试 Workflow 失败通知")
    notify.notify_workflow("test_workflow_002", "failed", {"error": "timeout"})

    print("\n3. 测试任务通知")
    notify.notify_task("task_12345", "promo", "tenant_1", "completed")

    print("\n✅ 测试完成（需要配置真实 webhook 地址才能收到消息）")


if __name__ == "__main__":
    test()
