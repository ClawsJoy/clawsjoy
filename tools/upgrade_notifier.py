#!/usr/bin/env python3
"""升级通知器 - 发送升级报告"""

import json
from datetime import datetime
from pathlib import Path


def send_notification(upgrade_record: dict):
    """发送升级通知（可扩展到邮件/钉钉/企业微信）"""

    message = f"""
    🤖 ClawsJoy 自我升级通知
    ========================
    Agent: {upgrade_record['agent']}
    时间: {upgrade_record['timestamp']}
    原成功率: {upgrade_record['success_rate_before']:.1%}
    改进: {upgrade_record['suggestions']}
    """

    print(message)

    # 保存到通知日志
    log_file = Path("logs/upgrade_notifications.log")
    log_file.parent.mkdir(exist_ok=True)
    with open(log_file, "a") as f:
        f.write(f"{datetime.now().isoformat()} - {upgrade_record['agent']} upgraded\n")

    # TODO: 添加邮件/webhook通知


if __name__ == "__main__":
    # 检查最近的升级
    history_file = Path("data/upgrades/upgrade_history.json")
    if history_file.exists():
        with open(history_file, "r") as f:
            history = json.load(f)
            if history:
                send_notification(history[-1])
