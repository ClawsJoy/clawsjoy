#!/usr/bin/env python3
"""文案生图 - 根据脚本内容生成配图"""

import requests
import urllib.parse
import uuid
import json
import re
from pathlib import Path
from datetime import datetime

IMAGE_DIR = Path("/mnt/d/clawsjoy/web/images/script_matched")

def extract_key_frames(script):
    """从脚本中提取关键画面描述"""
    frames = []
    
    # 匹配要点
    points = re.findall(r'(?:第一|第二|第三|第四|第五)([^。]+)', script)
    if points:
        frames = points[:5]
    else:
        # 按句子分割
        sentences = script.split('。')
        frames = [s.strip() for s in sentences if len(s.strip()) > 10][:5]
    
    return frames

def generate_image_from_text(text, style="realistic"):
    """根据文字生成图片"""
    if not text:
        return None
    
    prompt = f"Hong Kong, {text}, professional photography, 4k, {style}"
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=768"
    
    try:
        resp = requests.get(url, timeout=60)
        if resp.status_code == 200:
            IMAGE_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            img_name = f"match_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
            img_path = IMAGE_DIR / img_name
            with open(img_path, 'wb') as f:
                f.write(resp.content)
            print(f"✅ 生成: {text[:30]}...")
            return str(img_path)
    except Exception as e:
        print(f"❌ 生图失败: {e}")
    return None

def generate_matched_images(script):
    """根据脚本生成匹配的图片"""
    frames = extract_key_frames(script)
    
    if not frames:
        print("⚠️ 未能提取关键帧")
        return []
    
    images = []
    for i, frame in enumerate(frames):
        print(f"🎨 [{i+1}/{len(frames)}] 生成配图...")
        img = generate_image_from_text(frame)
        if img:
            images.append(img)
    
    # 保存映射
    mapping = {"script": script[:500], "images": images, "count": len(images)}
    with open(IMAGE_DIR / "mapping.json", 'w') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    
    return images

if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "第一：分数门槛降低。第二：人才清单新增。第三：审批时间缩短。"
    images = generate_matched_images(script)
    print(f"\n✅ 生成了 {len(images)} 张匹配图片")
    for img in images:
        print(f"   {img}")
