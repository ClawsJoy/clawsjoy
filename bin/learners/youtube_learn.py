#!/usr/bin/env python3
"""YouTube Agent 学习 - 学习上传和发布模式"""

import time
import re
from pathlib import Path

def learn_youtube_patterns():
    log_file = Path("/mnt/d/clawsjoy/logs/youtube_upload.log")
    if not log_file.exists():
        return
    
    with open(log_file) as f:
        logs = f.read()
    
    # 分析上传模式
    success = re.findall(r'✅.*上传成功', logs)
    if success:
        print(f"📹 YouTube学习: {len(success)} 次成功上传")

if __name__ == "__main__":
    while True:
        learn_youtube_patterns()
        time.sleep(7200)  # 2小时学习一次
