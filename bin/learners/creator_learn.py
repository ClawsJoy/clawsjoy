#!/usr/bin/env python3
"""内容创作 Agent 学习 - 学习内容风格和模板"""

import time
import json
from pathlib import Path

def learn_content_styles():
    video_dir = Path("/mnt/d/clawsjoy/web/videos")
    if not video_dir.exists():
        return
    
    videos = list(video_dir.glob("*.mp4"))
    print(f"🎬 创作学习: {len(videos)} 个视频已生成")

if __name__ == "__main__":
    while True:
        learn_content_styles()
        time.sleep(3600)
