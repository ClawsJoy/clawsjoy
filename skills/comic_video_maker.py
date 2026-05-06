#!/usr/bin/env python3
"""漫画风格视频合成器"""

import json
import subprocess
from pathlib import Path
from comic_generator import generate_comic_series, COMIC_DIR

VIDEO_DIR = Path("/mnt/d/clawsjoy/web/videos")

def make_comic_video(topic, script):
    """制作漫画风格视频"""
    
    # 1. 生成漫画分镜
    scenes = generate_comic_series()
    if not scenes:
        return None
    
    # 2. 准备 concat 文件
    video_name = f"comic_{topic}_{int(time.time())}.mp4"
    video_path = VIDEO_DIR / video_name
    concat_file = COMIC_DIR / "concat.txt"
    
    with open(concat_file, 'w') as f:
        for scene in scenes:
            f.write(f"file '{scene['image']}'\n")
            f.write(f"duration 3\n")
    
    # 3. 合成视频（无配音，留白给字幕）
    cmd = f'ffmpeg -f concat -safe 0 -i {concat_file} -vf "scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -pix_fmt yuv420p -y {video_path}'
    subprocess.run(cmd, shell=True)
    
    return str(video_path)

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "lion_rock"
    video = make_comic_video(topic, "")
    print(f"✅ 漫画视频: {video}")
