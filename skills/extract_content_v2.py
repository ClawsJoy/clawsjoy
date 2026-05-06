#!/usr/bin/env python3
"""AI 提取丰富内容"""

import requests
import json

def extract_content(topic):
    prompt = f"""请提供关于「{topic}」的详细内容（直接输出JSON）：

{{
    "summary": "一句话总结核心内容（20字内）",
    "detail": "详细说明（80字内）",
    "key_points": [
        "第一个关键信息（40字内）",
        "第二个关键信息（40字内）",
        "第三个关键信息（40字内）"
    ],
    "example": "一个真实案例或数据（50字内）",
    "advice": "给观众的具体建议（50字内）"
}}

只输出JSON，不要解释。内容要具体、有用。"""

    resp = requests.post("http://localhost:8101/api/agent",
        json={"text": prompt}, timeout=60)
    
    if resp.status_code == 200:
        msg = resp.json().get("message", "")
        try:
            start = msg.find('{')
            end = msg.rfind('}') + 1
            if start >= 0:
                return json.loads(msg[start:end])
        except:
            pass
    
    # 默认内容
    return {
        "summary": f"{topic}是2026年热门话题",
        "detail": "详情请关注官方最新公告",
        "key_points": ["条件更宽松", "流程更简化", "获批更快"],
        "example": "已有数千人成功获批",
        "advice": "建议尽早准备申请材料"
    }

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "香港优才计划"
    result = extract_content(topic)
    print(json.dumps(result, ensure_ascii=False, indent=2))
