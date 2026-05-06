#!/usr/bin/env python3
"""图片质量增强"""

import subprocess
from pathlib import Path

def enhance_image(img_path):
    """使用 ImageMagick 增强图片"""
    # 统一尺寸 1920x1080
    subprocess.run([
        'convert', img_path,
        '-resize', '1920x1080^',
        '-gravity', 'center',
        '-extent', '1920x1080',
        '-sharpen', '0x1',
        '-contrast',
        '-modulate', '100,120,100',
        img_path
    ], capture_output=True)
    return img_path

def batch_enhance(directory):
    """批量增强目录下所有图片"""
    for img in Path(directory).glob("*.jpg"):
        enhance_image(str(img))
        print(f"✅ 增强: {img.name}")

if __name__ == "__main__":
    batch_enhance("/mnt/d/clawsjoy/web/images")
