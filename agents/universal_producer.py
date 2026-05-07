#!/usr/bin/env python3
"""通用内容生产者 - 根据意图自动制作"""

import requests
import subprocess
from intent_parser import parse_intent

def produce(user_input):
    # 1. 解析意图
    intent = parse_intent(user_input)
    print(f"📍 地点: {intent['location']}")
    print(f"📌 主题: {intent['topic']}")
    print(f"🎨 风格: {intent['style']}")
    
    # 2. 生成标题
    title = f"{intent['location']}{intent['topic']}{intent['style']}解读"
    
    # 3. 生成脚本（调用 AI）
    prompt = f"写一篇300字的文章，介绍{intent['location']}的{intent['topic']}，风格{intent['style']}"
    result = subprocess.run(['ollama', 'run', 'llama3.2:3b', prompt], 
                           capture_output=True, text=True)
    script = result.stdout.strip()
    
    # 4. 制作视频
    resp = requests.post("http://localhost:8105/api/promo/make",
        json={"city": intent['location'], "topic": intent['topic'], "script": script})
    
    return resp.json()

if __name__ == "__main__":
    import sys
    user_input = sys.argv[1] if len(sys.argv) > 1 else "做个上海人才引进视频"
    result = produce(user_input)
    print(f"视频: {result.get('video_url')}")
