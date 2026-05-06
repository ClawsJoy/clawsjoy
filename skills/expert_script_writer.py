#!/usr/bin/env python3
"""专家级脚本生成器 - 模拟话题专家解读"""

import json
import requests
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"  # 使用更强模型

def load_expert_context(category, limit=5):
    """加载专家级上下文"""
    data_dir = Path(f"/mnt/d/clawsjoy/tenants/tenant_1/library/{category}")
    if not data_dir.exists():
        return []
    
    files = sorted(data_dir.glob("*.txt"), key=lambda x: x.stat().st_mtime, reverse=True)
    contents = []
    for f in files[:limit]:
        with open(f, 'r', encoding='utf-8') as fp:
            text = fp.read()[:2000]
            contents.append(f"【{f.stem}】\n{text}")
    return contents

def expert_analyze(topic, context):
    """专家分析模式"""
    
    expert_prompt = f"""你是一位资深的香港政策与生活专家，拥有10年+的行业经验。请基于以下资料，以专家视角分析{topic}。

【参考资料】
{chr(10).join(context)}

请以专家身份回答：
1. 核心解读（一句话总结）
2. 关键变化（3个要点）
3. 对普通人/申请人的影响
4. 专业建议
5. 风险提示（如有）

输出格式：纯文本，禁止使用任何标记符号（如###、***、**、[]等），直接输出解说词，每段标注标题。语气：专业、可靠、有洞察力。"""

    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": expert_prompt,
            "stream": False,
            "options": {"temperature": 0.4, "num_predict": 800}
        }, timeout=90)
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except Exception as e:
        print(f"专家分析错误: {e}")
    return ""

def expert_to_script(analysis, topic):
    """将专家分析转化为视频脚本"""
    
    script_prompt = f"""请将以下专家分析转化为一个3分钟的YouTube视频脚本。

专家分析内容：
{analysis}

脚本要求：
- 开场：用专家身份建立信任感
- 正文：3-4个核心观点，每个观点45秒
- 结尾：总结+行动建议
- 风格：专业但不枯燥，有温度

直接输出脚本："""

    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": script_prompt,
            "stream": False,
            "options": {"temperature": 0.6, "num_predict": 1200}
        }, timeout=90)
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except Exception as e:
        print(f"脚本生成错误: {e}")
    return ""

def generate_expert_script(topic, category="immigration"):
    """完整流程：专家分析 → 脚本"""
    print(f"📊 专家模式分析: {topic}")
    
    context = load_expert_context(category)
    print(f"📚 加载 {len(context)} 份资料")
    
    analysis = expert_analyze(topic, context)
    print(f"🔍 专家分析完成 ({len(analysis)} 字符)")
    
    script = expert_to_script(analysis, topic)
    print(f"📝 脚本生成完成 ({len(script)} 字符)")
    
    return script

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "香港优才计划2026"
    category = sys.argv[2] if len(sys.argv) > 2 else "immigration"
    
    script = generate_expert_script(topic, category)
    print("\n" + "="*50)
    print(script)
    
    # 保存
    from datetime import datetime
    output_file = Path(f"output/scripts/expert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(script)
    print(f"\n✅ 已保存: {output_file}")
