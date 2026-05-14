#!/usr/bin/env python3
"""可靠调度器 - 简化版"""

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

TASKS_BASE = Path("/mnt/d/clawsjoy/tasks")
TASKS = {
    "pending": TASKS_BASE / "pending",
    "running": TASKS_BASE / "running", 
    "done": TASKS_BASE / "done",
    "failed": TASKS_BASE / "failed",
}
for d in TASKS.values():
    d.mkdir(parents=True, exist_ok=True)

def log(msg):
    print(f"[{datetime.now()}] {msg}")

def run_task(name, cmd):
    log(f"执行: {name}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        log(f"✅ {name} 成功")
        return True
    else:
        log(f"❌ {name} 失败: {result.stderr[:100]}")
        return False

def main():
    log("🚀 调度器启动")
    
    # 每小时流水线
    while True:
        now = datetime.now()
        
        # 00分: 采集
        if now.minute == 0:
            run_task("采集", "cd /mnt/d/clawsjoy && python3 spiders/hk_spider.py")
            time.sleep(60)
        
        # 15分: 话题
        elif now.minute == 15:
            run_task("话题", "cd /mnt/d/clawsjoy && python3 skills/topic_planner/execute.py '{\"category\": \"all\"}'")
            time.sleep(60)
        
        # 30分: 脚本
        elif now.minute == 30:
            run_task("脚本", "cd /mnt/d/clawsjoy && python3 skills/script_from_data.py '香港优才计划'")
            time.sleep(60)
        
        # 45分: 视频
        elif now.minute == 45:
            run_task("视频", "cd /mnt/d/clawsjoy && curl -s -X POST http://localhost:8105/api/promo/make -H 'Content-Type: application/json' -d '{\"topic\":\"香港优才计划\"}'")
            time.sleep(60)
        
        time.sleep(30)

if __name__ == "__main__":
    main()
