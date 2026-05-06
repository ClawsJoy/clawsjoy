#!/usr/bin/env python3
"""测试 SD 图片生成"""

import requests
import base64
import json
from pathlib import Path

SD_API = "http://localhost:7860/sdapi/v1/txt2img"
OUTPUT_DIR = Path("/mnt/d/clawsjoy/web/images")

def generate_test_image():
    payload = {
        "prompt": "Hong Kong Victoria Harbour at night, city lights, professional photography, 4k",
        "negative_prompt": "blurry, low quality, watermark",
        "steps": 20,
        "width": 1024,
        "height": 768,
        "cfg_scale": 7
    }
    
    print("🎨 正在生成图片...")
    try:
        resp = requests.post(SD_API, json=payload, timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            img_data = base64.b64decode(data['images'][0])
            img_path = OUTPUT_DIR / "test_sd_generated.png"
            with open(img_path, 'wb') as f:
                f.write(img_data)
            print(f"✅ 图片已保存: {img_path}")
            print(f"   文件大小: {img_path.stat().st_size / 1024:.1f} KB")
        else:
            print(f"❌ 生成失败: {resp.status_code}")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    generate_test_image()
