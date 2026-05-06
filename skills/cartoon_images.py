#!/usr/bin/env python3
"""生成漫画风格人物图片"""

import requests
import uuid
from pathlib import Path

IMAGE_DIR = Path("/mnt/d/clawsjoy/web/images/cartoon")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

def generate_cartoon(character, style="motivational"):
    """生成卡通人物"""
    prompts = {
        "lion_rock": "Hong Kong Lion Rock spirit, motivational cartoon character, illustration style",
        "hk_worker": "Hong Kong worker cartoon character, hardworking, inspirational",
        "hk_student": "Hong Kong student cartoon character, studying hard, dream pursuit",
        "hk_elder": "Hong Kong elderly cartoon character, wisdom, traditional values"
    }
    
    prompt = prompts.get(character, prompts["lion_rock"])
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024"
    
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            img_name = f"{character}_{uuid.uuid4().hex[:8]}.jpg"
            img_path = IMAGE_DIR / img_name
            with open(img_path, 'wb') as f:
                f.write(resp.content)
            return str(img_path)
    except Exception as e:
        print(f"生成失败: {e}")
    return None

if __name__ == "__main__":
    for char in ["lion_rock", "hk_worker", "hk_student", "hk_elder"]:
        img = generate_cartoon(char)
        if img:
            print(f"✅ 生成: {img}")
