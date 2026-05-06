#!/usr/bin/env python3
"""生成2-3分钟的长脚本"""

import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_long_script(topic, context=""):
    prompt = f"""请为「{topic}」写一篇详细的解说词，时长约3分钟。

【要求】
- 字数：600-800字
- 结构：开场(60字) + 5-6个要点(每个100字) + 结尾(60字)
- 纯文本，无标记
- 语言流畅，适合配音

直接输出解说词："""

    resp = requests.post(OLLAMA_URL, json={
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "options": {
            "temperature": 0.6,
            "num_predict": 2500,
            "repeat_penalty": 1.1
        }
    }, timeout=120)
    
    if resp.status_code == 200:
        return resp.json().get("response", "")
    return ""

if __name__ == "__main__":
    topic = "香港优才计划2026"
    script = generate_long_script(topic)
    print(script)
    print(f"\n✅ 脚本长度: {len(script)} 字符", file=sys.stderr)
