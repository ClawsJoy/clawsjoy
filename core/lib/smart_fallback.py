#!/usr/bin/env python3
"""智能 Fallback - 让 Agent 在无法识别时用 LLM 引导用户"""

import requests
from typing import Optional


def smart_fallback(agent_name: str, user_input: str, description: str = "") -> str:
    """生成上下文感知的引导回复"""
    
    prompt = f"""用户说: "{user_input}"

我是 {agent_name}，{description}。

用户说的话我暂时无法直接处理（可能因为指令不完整、格式不对，或超出了我的能力范围）。

请用自然、友好的语气，引导用户重新描述需求。
- 不要用"我不知道"或"无法处理"
- 给出具体的可操作建议
- 使用问句引导用户

输出（直接回复用户，不要解释）："""

    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:1.5b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 80}
            },
            timeout=10
        )
        if resp.status_code == 200:
            reply = resp.json().get("response", "").strip()
            if reply:
                return reply
    except:
        pass
    
    # 降级：极简引导
    return f"💡 请告诉我更具体的信息，我会尽力帮你。比如：你想让我做什么？"


def smart_help(agent_name: str, capabilities: list) -> str:
    """生成简洁的能力说明"""
    caps = "、".join(capabilities[:4])
    return f"💡 {agent_name} 可以帮你 {caps}。需要我做什么？"
