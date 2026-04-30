#!/usr/bin/env python3
"""ClawsJoy Webhook 通知模块"""

import requests
import json
from datetime import datetime

class WebhookNotify:
    def __init__(self):
        self.webhooks = {
            "wechat": "",
            "dingtalk": "",
            "feishu": ""
        }
    
    def set_webhook(self, platform, url):
        self.webhooks[platform] = url
    
    def send_wechat(self, message):
        url = self.webhooks.get("wechat")
        if not url:
            return False
        try:
            resp = requests.post(url, json={"msgtype": "text", "text": {"content": message}}, timeout=5)
            return resp.status_code == 200
        except:
            return False
    
    def send_dingtalk(self, message):
        url = self.webhooks.get("dingtalk")
        if not url:
            return False
        try:
            resp = requests.post(url, json={"msgtype": "text", "text": {"content": message}}, timeout=5)
            return resp.status_code == 200
        except:
            return False
    
    def notify_workflow(self, workflow_id, status, result=None):
        emoji = "✅" if status == "completed" else "❌"
        message = f"{emoji} Workflow {workflow_id} 状态: {status}"
        if result:
            message += f"\n结果: {json.dumps(result, ensure_ascii=False)[:100]}"
        return self.send_wechat(message) or self.send_dingtalk(message)

if __name__ == "__main__":
    notify = WebhookNotify()
    print("Webhook 通知模块已加载")
