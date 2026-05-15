#!/usr/bin/env python3
"""资料库阅读器 - 让本地模型读取最新资料"""

import requests
import json
from pathlib import Path
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"
LIBRARY_BASE = Path("/mnt/d/clawsjoy/tenants/tenant_1/library")

def get_latest_files(category, limit=5):
    """获取最新的资料文件"""
    category_path = LIBRARY_BASE / category
    if not category_path.exists():
        return []
    
    files = sorted(category_path.glob("*.txt"), key=lambda x: x.stat().st_mtime, reverse=True)
    return files[:limit]

def read_file_content(filepath):
    """读取文件内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def build_context(files):
    """构建上下文（把资料喂给模型）"""
    context = "以下是最近采集的官方资料：\n\n"
    for i, f in enumerate(files, 1):
        content = read_file_content(f)
        # 只取前1500字，避免超长
        context += f"【资料{i}】\n{content[:1500]}\n\n---\n\n"
    return context

def generate_script_with_context(topic, context):
    """基于资料生成脚本"""
    prompt = f"""请基于以下最新资料，写一个3分钟的YouTube视频脚本。

{context}

脚本要求：
1. 必须基于上面提供的资料内容
2. 引用具体的数字和日期
3. 口语化，适合配音
4. 有开场、3个要点、结尾

主题：{topic}

直接输出脚本："""

    resp = requests.post(OLLAMA_URL, json={
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 1000}
    }, timeout=120)
    
    if resp.status_code == 200:
        return resp.json().get("response", "")
    return ""

def main():
    # 获取最新移民类资料
    files = get_latest_files("immigration", 3)
    
    if not files:
        print("没有找到资料")
        return
    
    print(f"📚 找到 {len(files)} 份最新资料")
    for f in files:
        print(f"   - {f.name}")
    
    # 构建上下文
    context = build_context(files)
    
    # 生成脚本
    topic = "香港人才引进最新政策"
    script = generate_script_with_context(topic, context)
    
    # 保存脚本
    output_file = f"output/scripts/rag_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(script)
    
    print(f"\n✅ 脚本已生成: {output_file}")
    print("\n" + "="*50)
    print(script[:500] + "...")
    return script

if __name__ == "__main__":
    main()
