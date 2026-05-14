"""环境交互 - 与其他系统、用户、工具交互"""

import subprocess
import requests
from datetime import datetime
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')

class EnvironmentInteraction:
    """环境交互器"""
    
    def __init__(self):
        self.interaction_log = []
    
    def notify_user(self, user_id, message, channel="api"):
        """通知用户"""
        if channel == "api":
            print(f"📢 通知用户 {user_id}: {message[:100]}")
            return {"success": True, "channel": "api", "message": message[:100]}
        
        return {"success": False, "error": f"Unknown channel: {channel}"}
    
    def execute_command(self, command, safe=True):
        """执行系统命令（安全模式）"""
        if safe:
            dangerous = ["rm -rf /", "sudo", "dd if=", "mkfs", ":(){:|:&};:"]
            for d in dangerous:
                if d in command:
                    return {"success": False, "error": f"Dangerous command blocked: {d}"}
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:500],
                "stderr": result.stderr[:200],
                "command": command[:100]
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def call_external_api(self, url, method="GET", data=None):
        """调用外部 API"""
        try:
            if method == "GET":
                resp = requests.get(url, timeout=30)
            elif method == "POST":
                resp = requests.post(url, json=data, timeout=30)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            return {
                "success": resp.status_code < 400,
                "status_code": resp.status_code,
                "data": resp.json() if resp.headers.get('content-type') == 'application/json' else resp.text[:500]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

environment = EnvironmentInteraction()
