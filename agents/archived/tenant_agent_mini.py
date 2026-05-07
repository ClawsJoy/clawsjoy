#!/usr/bin/env python3
"""TenantAgent 简化版 - 用于测试告警配置"""

import json
from pathlib import Path

class TenantAgent:
    def __init__(self, tenant_id="tenant_1"):
        self.tenant_id = tenant_id
        self.config_file = Path(f"/mnt/d/clawsjoy/tenants/{tenant_id}/agent_config.json")
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_config()
    
    def _load_config(self):
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.config = json.load(f)
        else:
            self.config = {"tenant_id": self.tenant_id, "alert_webhooks": {}, "preferences": {}}
    
    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def set_alert_webhook(self, platform, webhook_url):
        if "alert_webhooks" not in self.config:
            self.config["alert_webhooks"] = {}
        self.config["alert_webhooks"][platform] = webhook_url
        self._save_config()
        return {"success": True, "platform": platform}
    
    def get_alert_webhook(self, platform=None):
        if platform:
            return self.config.get("alert_webhooks", {}).get(platform)
        return self.config.get("alert_webhooks", {})
    
    def send_alert(self, message, title="ClawsJoy 告警"):
        import requests
        webhooks = self.get_alert_webhook()
        if not webhooks:
            return {"success": False, "error": "未配置告警渠道"}
        results = {}
        for platform, url in webhooks.items():
            try:
                if "dingtalk" in platform or "dingtalk" in url:
                    data = {"msgtype": "markdown", "markdown": {"title": title, "text": f"## {title}\n{message}"}}
                elif "feishu" in platform or "feishu" in url:
                    data = {"msg_type": "text", "content": {"text": f"[{title}]\n{message}"}}
                else:
                    data = {"msgtype": "markdown", "markdown": {"content": f"## {title}\n{message}"}}
                resp = requests.post(url, json=data, timeout=5)
                results[platform] = resp.status_code == 200
            except:
                results[platform] = False
        return results

if __name__ == "__main__":
    agent = TenantAgent("tenant_1")
    print(agent.set_alert_webhook("dingtalk", "https://oapi.dingtalk.com/robot/send?token=test"))
    print(agent.send_alert("测试消息"))
