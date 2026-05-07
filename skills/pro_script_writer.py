#!/usr/bin/env python3
"""专业 YouTube 脚本生成器 - 使用 qwen2.5:7b"""

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_pro_script(topic):
    prompt = f"""你是一个专业的YouTube香港生活博主。请写一个3分钟的视频脚本。

主题：{topic}

格式要求：
1. 开场（15秒）：抓人眼球
2. 要点1（45秒）：核心信息
3. 要点2（45秒）：深度分析  
4. 要点3（45秒）：实用建议
5. 结尾（30秒）：总结+引导

风格：口语化、有节奏、自然流畅

直接输出脚本："""

    # 使用更强的模型
    resp = requests.post(OLLAMA_URL, json={
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 800}
    }, timeout=90)
    
    if resp.status_code == 200:
        return resp.json().get("response", "")
    return ""

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "香港优才计划"
    script = generate_pro_script(topic)
    print(script)
