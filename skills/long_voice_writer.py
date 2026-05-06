#!/usr/bin/env python3
"""长篇配音脚本生成器"""

import json
import requests
from pathlib import Path
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"

def generate_long_script(topic, context):
    prompt = f"""请基于以下资料，写一篇详细的解说稿，用于3-4分钟的视频配音。

【资料】
{chr(10).join(context)[:3500]}

【要求】
1. 字数：1500-2000字
2. 结构：开场（60-80字）+ 6-8个要点（每个150-200字）+ 结尾（80-100字）
3. 每段5-8句话
4. 纯文本，无标记
5. 语言流畅，适合朗读

直接输出解说稿："""

    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.6,
                "num_predict": 3500,
                "repeat_penalty": 1.15,
                "top_k": 50
            }
        }, timeout=240)
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except Exception as e:
        print(f"错误: {e}")
    return ""

def load_context(category="immigration", limit=4):
    data_dir = Path(f"/mnt/d/clawsjoy/tenants/tenant_1/library/{category}")
    context = []
    if data_dir.exists():
        for f in list(data_dir.glob("*.txt"))[:limit]:
            with open(f, 'r') as fp:
                context.append(fp.read()[:1500])
    return context

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "香港优才计划2026"
    category = sys.argv[2] if len(sys.argv) > 2 else "immigration"
    
    print(f"📝 生成: {topic}", file=sys.stderr)
    context = load_context(category, 4)
    print(f"📚 资料: {len(context)} 份", file=sys.stderr)
    
    script = generate_long_script(topic, context)
    print(script)
    
    output = Path(f"output/scripts/long_voice_{int(time.time())}.txt")
    output.parent.mkdir(exist_ok=True)
    with open(output, 'w') as f:
        f.write(script)
    print(f"\n✅ 已保存: {output} ({len(script)} 字符)", file=sys.stderr)
