#!/usr/bin/env python3
"""关键词驱动全流程：采集 → 脚本 → 视频"""

import json
import requests
from keyword_driven_spider import execute as spider_execute

def produce_video(user_input):
    # 1. 关键词驱动采集
    print("📡 采集阶段")
    spider_result = spider_execute(user_input)
    
    if spider_result.get('error'):
        return {"error": spider_result['error']}
    
    city = spider_result['city']
    content = spider_result['content']
    
    # 2. 生成脚本
    print("✍️ 脚本阶段")
    prompt = f"根据以下资料，写一段2分钟的视频脚本：{content[:500]}"
    resp = requests.post("http://localhost:8101/api/agent",
        json={"text": prompt})
    script = resp.json().get("message", "")
    
    # 3. 制作视频
    print("🎬 视频阶段")
    video_resp = requests.post("http://localhost:8105/api/promo/make",
        json={"city": city, "script": script})
    
    return video_resp.json()

if __name__ == "__main__":
    import sys
    user_input = sys.argv[1] if len(sys.argv) > 1 else "香港优才计划"
    result = produce_video(user_input)
    print(f"视频: {result.get('video_url')}")
