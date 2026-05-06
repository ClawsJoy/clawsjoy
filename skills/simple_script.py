#!/usr/bin/env python3
"""简单脚本生成 - AI 只填空"""

import requests
import json

def generate_script(topic):
    prompt = f"""请为「{topic}」生成一段30秒口播文案，直接输出，不要解释，不要标点符号。

格式：一句话介绍 + 三个要点 + 一句建议

示例输出：
香港优才计划2026有重大变化。第一分数门槛降低。第二申请流程简化。第三获批时间缩短。建议尽早准备材料。"""

    resp = requests.post("http://localhost:8101/api/agent",
        json={"text": prompt}, timeout=60)
    
    if resp.status_code == 200:
        return resp.json().get("message", "")
    return ""

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "香港优才计划"
    script = generate_script(topic)
    print(script)
