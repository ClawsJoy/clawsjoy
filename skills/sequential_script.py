#!/usr/bin/env python3
"""逐段生成，每段继承上文，避免重复"""

import json
import requests
from pathlib import Path
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"

def load_context(category="immigration", limit=3):
    data_dir = Path(f"/mnt/d/clawsjoy/tenants/tenant_1/library/{category}")
    context = []
    if data_dir.exists():
        for f in list(data_dir.glob("*.txt"))[:limit]:
            with open(f, 'r') as fp:
                context.append(fp.read()[:1500])
    return context

def generate_script(topic, context, total_chars=2500):
    """一次性生成完整脚本（不分段）"""
    
    prompt = f"""请为「{topic}」写一份详细的解说词。

【资料】
{chr(10).join(context)[:3500]}

【要求】
- 总字数：1500-2000字
- 分为5-8个自然段落
- 纯文本，无标记
- 内容连贯，不重复
- 直接输出全文："""

    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.6,
                "num_predict": 3000,
                "repeat_penalty": 1.2,
                "top_k": 50
            }
        }, timeout=180)
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except Exception as e:
        print(f"错误: {e}")
    return ""

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "香港优才计划2026"
    category = sys.argv[2] if len(sys.argv) > 2 else "immigration"
    
    context = load_context(category, 4)
    print(f"📚 加载 {len(context)} 份资料", file=sys.stderr)
    
    script = generate_script(topic, context)
    
    # 去重检查（简单去重）
    lines = script.split('\n')
    unique_lines = []
    seen = set()
    for line in lines:
        if line.strip() and line.strip() not in seen:
            unique_lines.append(line)
            seen.add(line.strip())
        elif not line.strip():
            unique_lines.append(line)
    
    cleaned = '\n'.join(unique_lines)
    
    print(cleaned)
    
    output = Path("output/scripts/final_script.txt")
    with open(output, 'w') as f:
        f.write(cleaned)
    print(f"\n✅ 保存: {output} ({len(cleaned)} 字符)", file=sys.stderr)
    print(f"📊 去重前: {len(script)} 字符 → 去重后: {len(cleaned)} 字符", file=sys.stderr)
