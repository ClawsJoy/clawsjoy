"""通知 Agent"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agents.base_agent import BaseAgent

class NotificationAgent(BaseAgent):
    name = "notification_agent"
    description = "通知专家，发送各种类型的通知"
    capabilities = ["email_notification", "webhook", "desktop_notification"]
    skills = []
    
    def execute(self, params):
        operation = params.get("operation")
        message = params.get("message", "")
        
        if operation == "log":
            return self._log_notification(message)
        elif operation == "webhook":
            return self._send_webhook(params)
        else:
            return {"success": True, "message": f"通知: {message[:50]}"}
    
    def _log_notification(self, message):
        from datetime import datetime
        with open("logs/notifications.log", "a") as f:
            f.write(f"{datetime.now()}: {message}\n")
        return {"success": True, "logged": True}
    
    def _send_webhook(self, params):
        import requests
        url = params.get("url")
        if not url:
            return {"success": False, "error": "缺少 webhook URL"}
        try:
            resp = requests.post(url, json=params.get("data", {}), timeout=10)
            return {"success": resp.status_code == 200}
        except Exception as e:
            return {"success": False, "error": str(e)}

notification_agent = NotificationAgent()
