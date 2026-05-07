#!/usr/bin/env python3
"""监控指标收集器 - 轻量级"""

import json
import subprocess
import time
import socket
from pathlib import Path
from datetime import datetime

METRICS_FILE = Path("/mnt/d/clawsjoy/data/metrics.json")
ALERT_LOG = Path("/mnt/d/clawsjoy/logs/alerts.log")

def get_service_status():
    """检查所有服务状态"""
    services = {
        "chat-api": {"port": 18109, "pm2_name": "chat-api"},
        "promo-api": {"port": 8108, "pm2_name": "promo-api"},
        "agent-api": {"port": 18103, "pm2_name": "agent-api"},
        "web": {"port": 18083, "docker": "clawsjoy-web"},
        "redis": {"port": 16380, "docker": "clawsjoy-redis"},
        "tts": {"port": 19001, "docker": "clawsjoy-tts"},
        "ollama": {"port": 11434, "service": "ollama"},
        "meilisearch": {"port": 7700, "docker": "clawsjoy-meilisearch"},
        "qdrant": {"port": 6333, "docker": "clawsjoy-qdrant"},
    }
    
    status = {}
    for name, info in services.items():
        try:
            if "port" in info:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', info["port"]))
                sock.close()
                status[name] = {"status": "up" if result == 0 else "down", "port": info["port"]}
            elif "docker" in info:
                result = subprocess.run(["docker", "ps", "-q", "-f", f"name={info['docker']}"],
                                        capture_output=True, text=True)
                status[name] = {"status": "up" if result.stdout.strip() else "down"}
        except:
            status[name] = {"status": "unknown"}
    
    return status

def get_resource_usage():
    """资源使用情况"""
    try:
        # 磁盘使用
        df = subprocess.run(["df", "-h", "/mnt/d"], capture_output=True, text=True)
        disk_line = df.stdout.split('\n')[1]
        disk_usage = disk_line.split()[4].rstrip('%')
        
        # 内存使用
        free = subprocess.run(["free", "-m"], capture_output=True, text=True)
        mem_line = free.stdout.split('\n')[1]
        mem_used = int(mem_line.split()[2])
        mem_total = int(mem_line.split()[1])
        
        return {
            "disk_usage_percent": int(disk_usage),
            "memory_used_mb": mem_used,
            "memory_total_mb": mem_total,
            "memory_percent": round(mem_used / mem_total * 100, 1)
        }
    except:
        return {}

def get_pm2_status():
    """PM2 进程状态"""
    try:
        result = subprocess.run(["pm2", "jlist"], capture_output=True, text=True)
        processes = json.loads(result.stdout)
        return {p["name"]: {"status": p["pm2_env"]["status"], "restarts": p["pm2_env"]["restart_time"]} 
                for p in processes}
    except:
        return {}

def collect_metrics():
    """收集所有指标"""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "services": get_service_status(),
        "resources": get_resource_usage(),
        "pm2": get_pm2_status()
    }
    
    # 保存到文件
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    return metrics

def check_alerts(metrics):
    """检查并触发告警"""
    alerts = []
    
    # 1. 服务 down 告警
    for name, status in metrics["services"].items():
        if status.get("status") == "down":
            alerts.append(f"⚠️ 服务 {name} 不可用 (端口 {status.get('port', '?')})")
    
    # 2. 资源告警
    res = metrics.get("resources", {})
    if res.get("disk_usage_percent", 0) > 85:
        alerts.append(f"💾 磁盘使用率 {res['disk_usage_percent']}% > 85%")
    if res.get("memory_percent", 0) > 90:
        alerts.append(f"🧠 内存使用率 {res['memory_percent']}% > 90%")
    
    # 3. PM2 进程异常重启
    for name, info in metrics.get("pm2", {}).items():
        if info.get("restarts", 0) > 10:
            alerts.append(f"🔄 PM2 进程 {name} 已重启 {info['restarts']} 次")
    
    # 记录告警
    if alerts:
        with open(ALERT_LOG, 'a') as f:
            f.write(f"{metrics['timestamp']}\n")
            for alert in alerts:
                f.write(f"  {alert}\n")
            f.write("\n")
        print(f"📢 触发 {len(alerts)} 条告警")
    
    return alerts

if __name__ == "__main__":
    metrics = collect_metrics()
    alerts = check_alerts(metrics)
    
    # 如果有严重告警，可以通过 Webhook 发送（可选）
    if alerts and len(alerts) >= 3:
        # TODO: 发送到你的通知渠道（钉钉/企微/飞书）
        pass
    
    # 输出简要状态
    up = sum(1 for s in metrics["services"].values() if s.get("status") == "up")
    total = len(metrics["services"])
    print(f"📊 {up}/{total} 服务正常 | 磁盘 {metrics['resources'].get('disk_usage_percent', '?')}%")
