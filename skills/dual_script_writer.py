#!/usr/bin/env python3
"""生成分离的配音脚本和分镜剧本"""

import json
import requests
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"

def generate_dual_script(topic, context):
    """生成配音脚本和分镜剧本"""
    
    prompt = f"""请基于以下资料，为「{topic}」生成两种脚本。

【参考资料】
{chr(10).join(context)}

请输出以下格式，两种脚本用 "===SPLIT===" 分隔：

【配音脚本】
纯解说词，不要任何标注、不要时间码、不要画面描述、不要标记符号。可直接用于TTS朗读。

===SPLIT===

【分镜剧本】
包含时间码和画面描述，格式如下：
[00:00-00:15] 画面：... 解说：...
[00:15-00:45] 画面：... 解说：...
[00:45-01:30] 画面：... 解说：...
"""

    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.5, "num_predict": 1500}
        }, timeout=120)
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except Exception as e:
        print(f"生成错误: {e}")
    return ""

def extract_voice_script(full_output):
    """提取配音脚本"""
    if "===SPLIT===" in full_output:
        parts = full_output.split("===SPLIT===")
        return parts[0].replace("【配音脚本】", "").strip()
    return full_output

def extract_storyboard(full_output):
    """提取分镜剧本"""
    if "===SPLIT===" in full_output:
        parts = full_output.split("===SPLIT===")
        return parts[1].replace("【分镜剧本】", "").strip()
    return ""

# ... 省略 load_context 函数 ...
