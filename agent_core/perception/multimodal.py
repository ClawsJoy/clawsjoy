"""多模态感知 - 文本、图像、声音、系统状态"""

import subprocess
import requests
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')

class MultimodalPerception:
    """多模态感知器"""
    
    def __init__(self):
        self.perception_log = Path("data/perception_log.json")
        self._init_log()
    
    def _init_log(self):
        if not self.perception_log.exists():
            with open(self.perception_log, 'w') as f:
                json.dump({"perceptions": []}, f)
    
    def perceive_text(self, text):
        """感知文本内容"""
        return {
            "type": "text",
            "content": text,
            "length": len(text),
            "timestamp": datetime.now().isoformat()
        }
    
    def perceive_system(self):
        """感知系统状态"""
        # CPU 使用率
        cpu = subprocess.run("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'", 
                             shell=True, capture_output=True, text=True)
        
        # 内存使用
        mem = subprocess.run("free -m | grep Mem | awk '{print $3\"/\"$2}'", 
                             shell=True, capture_output=True, text=True)
        
        # 磁盘
        disk = subprocess.run("df -h / | tail -1 | awk '{print $5}'", 
                              shell=True, capture_output=True, text=True)
        
        # 进程数
        procs = subprocess.run("ps aux | wc -l", 
                               shell=True, capture_output=True, text=True)
        
        return {
            "type": "system",
            "cpu": cpu.stdout.strip(),
            "memory": mem.stdout.strip(),
            "disk": disk.stdout.strip(),
            "processes": int(procs.stdout.strip()),
            "timestamp": datetime.now().isoformat()
        }
    
    def perceive_network(self):
        """感知网络状态"""
        # 检查关键服务
        services = {
            "ollama": "http://localhost:11434/api/tags",
            "gateway": "http://localhost:5002/api/health",
            "fileservice": "http://localhost:5003/health",
            "multiagent": "http://localhost:5006/health"
        }
        
        status = {}
        for name, url in services.items():
            try:
                resp = requests.get(url, timeout=3)
                status[name] = "up" if resp.status_code == 200 else "down"
            except:
                status[name] = "down"
        
        return {
            "type": "network",
            "services": status,
            "timestamp": datetime.now().isoformat()
        }
    
    def perceive_all(self):
        """全面感知"""
        perceptions = {
            "system": self.perceive_system(),
            "network": self.perceive_network(),
            "timestamp": datetime.now().isoformat()
        }
        
        # 记录感知
        with open(self.perception_log, 'r') as f:
            log = json.load(f)
        log["perceptions"].append(perceptions)
        log["perceptions"] = log["perceptions"][-100:]  # 保留最近100条
        with open(self.perception_log, 'w') as f:
            json.dump(log, f, indent=2)
        
        return perceptions
    
    def detect_anomalies(self):
        """检测异常"""
        perceptions = self.perceive_all()
        anomalies = []
        
        # 检查服务状态
        for service, status in perceptions["network"]["services"].items():
            if status == "down":
                anomalies.append(f"服务 {service} 不可用")
        
        # 检查磁盘
        disk_usage = perceptions["system"]["disk"].replace('%', '')
        if disk_usage.isdigit() and int(disk_usage) > 85:
            anomalies.append(f"磁盘使用率 {disk_usage}%")
        
        return anomalies

perception = MultimodalPerception()

if __name__ == '__main__':
    print("🔍 系统感知:", perception.perceive_all())
    print("\n⚠️ 异常检测:", perception.detect_anomalies())
