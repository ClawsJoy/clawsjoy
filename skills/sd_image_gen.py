#!/usr/bin/env python3
"""Stable Diffusion 图片生成 - 夜间任务"""

import requests
import json
import base64
import uuid
from pathlib import Path
from datetime import datetime

SD_API = "http://localhost:7860/sdapi/v1/txt2img"
IMAGE_DIR = Path("/mnt/d/clawsjoy/web/images/sd_generated")

def generate_image(prompt, negative_prompt="", width=1024, height=768):
    """生成单张图片"""
    payload = {
        "prompt": f"{prompt}, 4k, high quality, Hong Kong style",
        "negative_prompt": f"blurry, low quality, watermark, text, {negative_prompt}",
        "steps": 25,
        "width": width,
        "height": height,
        "cfg_scale": 7,
        "sampler_index": "Euler a"
    }
    
    try:
        resp = requests.post(SD_API, json=payload, timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            img_data = base64.b64decode(data['images'][0])
            img_name = f"{uuid.uuid4().hex}.png"
            img_path = IMAGE_DIR / img_name
            with open(img_path, 'wb') as f:
                f.write(img_data)
            return str(img_path)
    except Exception as e:
        print(f"SD 生成失败: {e}")
    return None

def batch_generate_for_topics(topics):
    """批量为话题生成图片"""
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    results = {}
    for topic in topics:
        print(f"🎨 生成图片: {topic}")
        prompt = f"Hong Kong {topic}, professional photography, cinematic lighting"
        img_path = generate_image(prompt)
        if img_path:
            results[topic] = img_path
            print(f"✅ 保存: {img_path}")
    
    # 保存映射表
    with open(IMAGE_DIR / "image_mapping.json", 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results

if __name__ == "__main__":
    # 预生成香港相关话题图片
    topics = [
        "skyline night view",
        "financial district",
        "harbour view",
        "university campus",
        "innovation technology",
        "cultural heritage"
    ]
    batch_generate_for_topics(topics)
