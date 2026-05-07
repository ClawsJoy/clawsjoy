#!/usr/bin/env python3
"""YouTube 自动发布 Skill"""
import subprocess
import json
from pathlib import Path

def execute(params):
    video_path = params.get('video_path')
    title = params.get('title', 'ClawsJoy 自动生成视频')
    description = params.get('description', '由 ClawsJoy AI 自动生成')
    tags = params.get('tags', 'AI,自动生成')
    
    if not video_path or not Path(video_path).exists():
        return {"success": False, "error": "视频文件不存在"}
    
    cmd = [
        "python3", "/mnt/d/clawsjoy/agents/youtube_uploader.py",
        "--video", video_path,
        "--title", title,
        "--description", description,
        "--tags", tags
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {"success": result.returncode == 0, "output": result.stdout}
