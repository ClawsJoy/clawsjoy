#!/usr/bin/env python3
import subprocess
import json
import os
from pathlib import Path

def make_promo(city, tenant_id):
    img_dir = f"/home/flybo/clawsjoy/web/images/{city}"
    output_dir = "/home/flybo/clawsjoy/web/videos"
    output_file = f"{output_dir}/{city}_promo_{os.popen('date +%s').read().strip()}.mp4"
    
    # 查找第一张图片
    images = list(Path(img_dir).glob("*.jpg")) + list(Path(img_dir).glob("*.png"))
    if not images:
        return {"success": False, "error": "No images found"}
    
    # 直接用 ffmpeg 生成 15 秒视频
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(images[0]),
        "-c:v", "libx264", "-t", "15",
        "-pix_fmt", "yuv420p", "-vf", "scale=1920:1080",
        output_file
    ]
    result = subprocess.run(cmd, capture_output=True)
    
    if result.returncode == 0 and os.path.exists(output_file):
        return {
            "success": True,
            "video_url": f"/videos/{os.path.basename(output_file)}"
        }
    return {"success": False, "error": "Video generation failed"}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = make_promo(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "1")
        print(json.dumps(result))
