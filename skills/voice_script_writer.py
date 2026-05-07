#!/usr/bin/env python3
"""纯配音脚本生成器 - 长文本版"""

import json
import requests
from pathlib import Path
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"

def generate_voice_script(topic, context):
    """生成长篇配音脚本"""
    
    prompt = f"""请基于以下资料，为「{topic}」生成一段3-4分钟的详细解说词。

【参考资料】
{chr(10).join(context)[:3000]}

【要求】
- 纯文本，不要任何标记符号
- 不要时间码、不要画面描述
- 内容要详细，分5-8个段落
- 每段5-8句话
- 总长度800-1200字

直接输出解说词："""

    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.5,
                "num_predict": 3500,  # 增加到2000
                "repeat_penalty": 1.1
            }
        }, timeout=180)
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except Exception as e:
        print(f"生成错误: {e}")
    return ""

def load_context(category="immigration", limit=3):
    """加载资料"""
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
    
    print(f"📝 生成脚本: {topic}", file=sys.stderr)
    context = load_context(category)
    print(f"📚 加载 {len(context)} 份资料", file=sys.stderr)
    
    script = generate_voice_script(topic, context)
    print(script)
    
    # 保存
    output_file = Path(f"output/scripts/voice_{int(time.time())}.txt")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(script)
    print(f"\n✅ 脚本已保存: {output_file} ({len(script)} 字符)", file=sys.stderr)
