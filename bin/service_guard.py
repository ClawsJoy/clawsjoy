#!/usr/bin/env python3
"""服务守护进程 - 自动重启失败的服务"""

import subprocess
import time
import requests
from datetime import datetime

SERVICES = [
    {"name": "main_gateway", "port": 5002, "cmd": "python3 agent_gateway_web.py"},
    {"name": "file_service", "port": 5003, "cmd": "python3 file_service_complete.py"},
    {"name": "doc_generator", "port": 5004, "cmd": "python3 doc_generator.py"},
    {"name": "multi_agent", "port": 5006, "cmd": "python3 multi_agent_service_v2.py"},
]

def check_service(port, name):
    try:
        resp = requests.get(f"http://localhost:{port}/health", timeout=3)
        return resp.status_code == 200
    except:
        return False

def restart_service(cmd, name):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 重启 {name}...")
    subprocess.run(f"pkill -f '{cmd.split()[-1]}'", shell=True)
    time.sleep(1)
    subprocess.Popen(cmd, shell=True, cwd="/mnt/d/clawsjoy")
    return True

def main():
    print("🛡️ 服务守护进程启动")
    print("="*50)
    
    while True:
        for svc in SERVICES:
            if not check_service(svc["port"], svc["name"]):
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ {svc['name']} 异常")
                restart_service(svc["cmd"], svc["name"])
                time.sleep(2)
        time.sleep(30)

if __name__ == "__main__":
    main()
