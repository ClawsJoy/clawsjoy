#!/usr/bin/env python3
"""基于采集资料生成脚本"""

import json
import time
import requests
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
DATA_DIR = Path("/mnt/d/clawsjoy/tenants/tenant_1/library")


def load_latest_data(category, limit=3):
    """加载最新的采集资料"""
    category_dir = DATA_DIR / category
    if not category_dir.exists():
        return []
    
    files = sorted(category_dir.glob("*.txt"), key=lambda x: x.stat().st_mtime, reverse=True)
    contents = []
    for f in files[:limit]:
        with open(f, 'r', encoding='utf-8') as fp:
            contents.append(f"【{f.stem}】\n{fp.read()[:1500]}")
    return contents


def generate_script(topic, context_data):
    """基于资料生成脚本"""
    context = "\n\n---\n\n".join(context_data) if context_data else "无历史资料"
    
    prompt = f"""你是一个专业的香港内容博主。请基于以下资料，写一个3分钟的YouTube视频脚本。

【参考资料】
{context}

【主题】{topic}

【脚本要求】
1. 开场：吸引人的Hook（15秒）
2. 正文：3-4个要点，每个要点45秒
3. 结尾：总结+互动引导（30秒）
4. 风格：口语化、有网感

直接输出脚本："""

    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.6, "num_predict": 1200}
        }, timeout=90)
        
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except Exception as e:
        print(f"生成错误: {e}")
    
    return ""


if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "香港优才计划"
    
    print(f"📝 生成脚本: {topic}")
    print("=" * 50)
    
    # 根据话题选择资料类别
    if any(k in topic for k in ["优才", "高才", "人才", "移民"]):
        category = "immigration"
    elif any(k in topic for k in ["留学", "大学", "教育"]):
        category = "education"
    else:
        category = "news"
    
    context = load_latest_data(category)
    print(f"📚 加载 {len(context)} 份资料")
    
    script = generate_script(topic, context)
    print(script)
    
    # 保存脚本
    output_dir = Path("output/scripts")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"script_{int(time.time())}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(script)
    print(f"\n✅ 脚本已保存: {output_file}")
