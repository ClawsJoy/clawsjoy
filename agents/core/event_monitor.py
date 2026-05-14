from lib.unified_config import config
#!/usr/bin/env python3
"""事件驱动监控 - 实时触发自愈"""

import time
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path
import threading
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')

class EventMonitor:
    def __init__(self):
        self.running = True
        self.alert_file = Path("data/alerts.json")
        self._init_alert_file()
    
    def _init_alert_file(self):
        if not self.alert_file.exists():
            with open(self.alert_file, 'w') as f:
                json.dump({"alerts": []}, f)
    
    def log_alert(self, alert_type, message, severity):
        """记录告警"""
        with open(self.alert_file, 'r') as f:
            data = json.load(f)
        
        data["alerts"].append({
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })
        
        # 只保留最近100条
        data["alerts"] = data["alerts"][-100:]
        
        with open(self.alert_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # 触发自愈
        self.trigger_healing(alert_type, message)
    
    def trigger_healing(self, alert_type, message):
        """触发自愈 Agent"""
        print(f"🔔 触发自愈: {alert_type} - {message[:50]}")
        result = subprocess.run(
            ["python3", "agents/llm_healer.py"],
            capture_output=True, text=True,
            cwd="/mnt/d/clawsjoy"
        )
        return result.returncode == 0
    
    def check_api_health(self):
        """持续检查 API 健康"""
        consecutive_failures = 0
        while self.running:
            try:
                resp = requests.get('http://localhost:5002/api/health', timeout=5)
                if resp.status_code != 200:
                    consecutive_failures += 1
                    if consecutive_failures >= 3:
                        self.log_alert("api_unhealthy", f"API 连续 {consecutive_failures} 次异常", "high")
                        consecutive_failures = 0
                else:
                    consecutive_failures = 0
            except:
                consecutive_failures += 1
                if consecutive_failures >= 3:
                    self.log_alert("api_down", f"API 连续 {consecutive_failures} 次无响应", "critical")
                    consecutive_failures = 0
            
            time.sleep(30)  # 每30秒检查一次
    
    def check_ollama_health(self):
        """持续检查 Ollama 健康"""
        consecutive_failures = 0
        while self.running:
            try:
                resp = requests.get('http://localhost:11434/api/tags', timeout=5)
                if resp.status_code != 200:
                    consecutive_failures += 1
                    if consecutive_failures >= 2:
                        self.log_alert("ollama_unhealthy", f"Ollama 连续 {consecutive_failures} 次异常", "high")
                        consecutive_failures = 0
                else:
                    consecutive_failures = 0
            except:
                consecutive_failures += 1
                if consecutive_failures >= 2:
                    self.log_alert("ollama_down", "Ollama 服务中断", "critical")
                    consecutive_failures = 0
            
            time.sleep(60)  # 每分钟检查一次
    
    def check_disk_space(self):
        """持续检查磁盘空间"""
        while self.running:
            result = subprocess.run("df -h / | tail -1 | awk '{print $5}'", 
                                    shell=True, capture_output=True, text=True)
            usage = result.stdout.strip().replace('%', '')
            if usage.isdigit() and int(usage) > 85:
                self.log_alert("disk_high", f"磁盘使用率 {usage}%", "high")
            elif usage.isdigit() and int(usage) > 90:
                self.log_alert("disk_critical", f"磁盘使用率 {usage}%", "critical")
            
            time.sleep(300)  # 每5分钟检查一次
    
    def start(self):
        """启动所有监控线程"""
        print("👁️ 事件监控服务启动")
        print("   监控项: API、Ollama、磁盘空间")
        
        threads = [
            threading.Thread(target=self.check_api_health, daemon=True),
            threading.Thread(target=self.check_ollama_health, daemon=True),
            threading.Thread(target=self.check_disk_space, daemon=True),
        ]
        
        for t in threads:
            t.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            print("\n监控服务停止")

if __name__ == '__main__':
    monitor = EventMonitor()
    monitor.start()
