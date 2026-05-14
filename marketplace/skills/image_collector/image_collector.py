"""图片采集技能 - 从 Unsplash 或占位图服务采集"""

from typing import Dict, List
from skills.skill_interface import BaseSkill
import requests
import os
import random

class ImageCollectorSkill(BaseSkill):
    name = "image_collector"
    description = "采集图片（支持 Unsplash API，降级到 Lorem Picsum）"
    version = "1.0.0"
    category = "content"
    
    def execute(self, params: Dict) -> Dict:
        keyword = params.get("keyword", params.get("topic", "city"))
        limit = params.get("limit", 10)
        width = params.get("width", 1920)
        height = params.get("height", 1080)
        
        images = []
        
        # 方案1: Unsplash API（需要 API Key）
        unsplash_key = os.getenv("UNSPLASH_KEY", "")
        if unsplash_key:
            try:
                resp = requests.get(
                    "https://api.unsplash.com/search/photos",
                    headers={"Authorization": f"Client-ID {unsplash_key}"},
                    params={"query": keyword, "per_page": limit},
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for img in data.get('results', []):
                        images.append({
                            "id": img['id'],
                            "url": img['urls']['regular'],
                            "thumbnail": img['urls']['thumb'],
                            "credit": f"Photo by {img['user']['name']} on Unsplash"
                        })
            except Exception as e:
                print(f"Unsplash API 失败: {e}")
        
        # 方案2: 降级到 Lorem Picsum（免费占位图）
        if not images:
            for i in range(limit):
                images.append({
                    "id": f"picsum_{i}",
                    "url": f"https://picsum.photos/id/{random.randint(1, 200)}/{width}/{height}",
                    "credit": "Placeholder image from picsum.photos"
                })
        
        return {
            "success": True,
            "images": images,
            "count": len(images),
            "keyword": keyword,
            "source": "unsplash" if unsplash_key else "picsum"
        }

skill = ImageCollectorSkill()

# 添加完整的错误处理
# 确保所有路径都存在
# 确保返回格式统一
