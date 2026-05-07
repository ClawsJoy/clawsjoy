#!/usr/bin/env python3
"""AI 提取内容要点，不生成完整脚本"""

import requests
import json

def extract_content(topic):
    prompt = f"""请提供关于「{topic}」的以下信息：

1. 核心政策/内容（50字内）
2. 3个关键要点（每个20字内）
3. 一个成功案例/数据（30字内）
4. 给观众的建议（30字内）

直接输出JSON格式：
{{"summary": "...", "key_points": ["...", "...", "..."], "example": "...", "advice": "..."}}"""

    resp = requests.post("http://localhost:8101/api/agent",
        json={"text": prompt}, timeout=60)
    
    if resp.status_code == 200:
        msg = resp.json().get("message", "")
        # 尝试提取JSON
        try:
            start = msg.find('{')
            end = msg.rfind('}') + 1
            if start >= 0:
                return json.loads(msg[start:end])
        except:
            pass
    return {"summary": topic, "key_points": ["要点1", "要点2", "要点3"], "example": "", "advice": ""}

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "香港优才计划"
    result = extract_content(topic)
    print(json.dumps(result, ensure_ascii=False, indent=2))
