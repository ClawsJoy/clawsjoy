#!/usr/bin/env python3
"""独立工程师学习进程"""

import time
import re
from pathlib import Path

def learn_from_errors():
    log_dir = Path("/mnt/d/clawsjoy/logs")
    error_patterns = {}
    
    for log_file in log_dir.glob("*.log"):
        if log_file.stat().st_size > 0:
            with open(log_file) as f:
                content = f.read()[-5000:]
            errors = re.findall(r'ERROR|Error|Exception|failed', content)
            for err in errors:
                error_patterns[err] = error_patterns.get(err, 0) + 1
    
    high_freq = {k: v for k, v in error_patterns.items() if v > 3}
    if high_freq:
        print(f"🔧 高频错误: {list(high_freq.keys())[:5]}")

if __name__ == "__main__":
    while True:
        try:
            learn_from_errors()
        except Exception as e:
            print(f"错误: {e}")
        time.sleep(600)  # 10分钟
    # 使用 sudo 执行重启命令
    import subprocess
    result = subprocess.run(['sudo', 'pm2', 'restart', 'all'], capture_output=True)
