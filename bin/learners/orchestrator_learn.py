#!/usr/bin/env python3
"""编排 Agent 学习 - 学习任务执行模式"""

import time
import re
from pathlib import Path

def learn_task_patterns():
    log_file = Path("/mnt/d/clawsjoy/logs/system.log")
    if not log_file.exists():
        return
    
    with open(log_file) as f:
        logs = f.read()
    
    # 分析任务模式
    task_patterns = re.findall(r'执行.*?任务|开始.*?工作流', logs)
    if task_patterns:
        print(f"📋 编排学习: 发现 {len(task_patterns)} 个任务模式")

if __name__ == "__main__":
    while True:
        learn_task_patterns()
        time.sleep(1800)
