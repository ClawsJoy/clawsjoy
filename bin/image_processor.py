#!/usr/bin/env python3
"""图片处理模块 - 集成到视频生成工作流"""

import subprocess
from pathlib import Path

def process_image(image_path):
    """统一处理图片：尺寸+对比度+锐化+色彩"""
    
    cmd = f"""convert {image_path} \
        -resize 1920x1080^ -gravity center -extent 1920x1080 \
        -contrast -sharpen 0x1 \
        -modulate 100,120,100 \
        {image_path}"""
    
    subprocess.run(cmd, shell=True, capture_output=True)
    return image_path

def batch_process_images(image_dir):
    """批量处理目录下所有图片"""
    for img in Path(image_dir).glob("*.jpg"):
        process_image(str(img))
        print(f"✅ 已处理: {img.name}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        batch_process_images(sys.argv[1])
