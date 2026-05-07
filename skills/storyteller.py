#!/usr/bin/env python3
"""讲故事模式 - 简化版"""

import sys
import requests
import time
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_story(topic):
    prompt = f"""用讲故事的方式介绍「{topic}」。200-300字。

要求：
- 从一个普通人视角
- 有情节，自然流畅
- 直接输出故事，不要解释"""

    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "options": {"num_predict": 800}
        }, timeout=60)
        
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
    return ""

if __name__ == "__main__":
    topic = "香港优才计划"
    story = generate_story(topic)
    print(story)
    
    # 保存
    output_file = Path(f"output/scripts/story_{int(time.time())}.txt")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(story)
    
    print(f"✅ 已保存: {output_file}", file=sys.stderr)
