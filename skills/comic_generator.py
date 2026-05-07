#!/usr/bin/env python3
"""图文漫画风格生成器"""

import requests
import uuid
import json
from pathlib import Path

COMIC_DIR = Path("/mnt/d/clawsjoy/web/images/comic")
COMIC_DIR.mkdir(parents=True, exist_ok=True)

# 漫画分镜模板
COMIC_SCENES = {
    "opening": {
        "prompt": "Hong Kong Lion Rock mountain landscape, comic book style, dramatic sky, inspirational",
        "caption": "狮子山——香港精神的象征"
    },
    "struggle": {
        "prompt": "Hong Kong people climbing mountain together, teamwork, comic illustration, motivational",
        "caption": "携手共进，永不言弃"
    },
    "success": {
        "prompt": "Hong Kong city skyline sunrise, comic art style, hopeful, vibrant colors",
        "caption": "狮子山下，共创未来"
    },
    "character": {
        "prompt": "Hong Kong elderly wise man cartoon character, traditional Chinese painting style",
        "caption": "老一辈的狮子山精神"
    },
    "youth": {
        "prompt": "Young Hong Kong people smiling, comic portrait, energetic, colorful",
        "caption": "新一代的传承"
    }
}

def generate_comic_scene(scene_key):
    """生成漫画分镜"""
    scene = COMIC_SCENES.get(scene_key, COMIC_SCENES["opening"])
    url = f"https://image.pollinations.ai/prompt/{scene['prompt']}?width=1024&height=768"
    
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            img_name = f"comic_{scene_key}_{uuid.uuid4().hex[:8]}.jpg"
            img_path = COMIC_DIR / img_name
            with open(img_path, 'wb') as f:
                f.write(resp.content)
            return {
                "image": str(img_path),
                "caption": scene["caption"],
                "prompt": scene["prompt"]
            }
    except Exception as e:
        print(f"生成失败: {scene_key}, {e}")
    return None

def generate_comic_series():
    """生成整套漫画分镜"""
    results = []
    for scene_key in COMIC_SCENES.keys():
        print(f"🎨 生成漫画分镜: {scene_key}")
        result = generate_comic_scene(scene_key)
        if result:
            results.append(result)
    return results

if __name__ == "__main__":
    scenes = generate_comic_series()
    print(f"✅ 生成了 {len(scenes)} 个漫画分镜")
    for s in scenes:
        print(f"   {s['caption']}: {s['image']}")
