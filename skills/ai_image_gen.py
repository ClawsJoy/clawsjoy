#!/usr/bin/env python3
"""AI 图片生成 - Pollinations（稳定版）"""

import requests
import urllib.parse
import uuid
from pathlib import Path
from datetime import datetime

IMAGE_DIR = Path("/mnt/d/clawsjoy/web/images/ai_generated")

def generate_image(prompt, width=1024, height=768):
    """生成图片"""
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}"
    
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            IMAGE_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            img_name = f"{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
            img_path = IMAGE_DIR / img_name
            with open(img_path, 'wb') as f:
                f.write(resp.content)
            return str(img_path)
    except Exception as e:
        print(f"生图失败: {e}")
    return None

def generate_hk_scenes():
    """生成香港系列图片"""
    scenes = [
        "Hong Kong Victoria Harbour night view, professional photography, 4k",
        "Hong Kong financial district skyscrapers, cinematic lighting",
        "Hong Kong university campus, modern architecture, sunny day",
        "Hong Kong traditional street market, vibrant colors",
        "Hong Kong cultural heritage site, historical building",
        "Hong Kong innovation technology park, futuristic design"
    ]
    
    images = []
    for scene in scenes:
        print(f"🎨 生成: {scene[:40]}...")
        img = generate_image(scene)
        if img:
            images.append(img)
            print(f"   ✅ 保存: {img}")
    
    # 保存图片列表供视频使用
    import json
    with open(IMAGE_DIR / "image_list.json", 'w') as f:
        json.dump(images, f)
    
    return images

if __name__ == "__main__":
    images = generate_hk_scenes()
    print(f"\n✅ 生成了 {len(images)} 张图片")
    for img in images:
        print(f"   {img}")
