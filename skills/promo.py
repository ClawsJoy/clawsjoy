#!/usr/bin/env python3
"""宣传片制作技能 - 通过关键词驱动"""

import json
import sys
import requests

def execute(params):
    # 关键词提取
    topic = params.get('topic', params.get('city', '香港'))
    keywords = params.get('keywords', '')
    
    # 调用 Promo API
    try:
        resp = requests.post(
            "http://localhost:8108/api/promo/make",
            json={"topic": topic, "keywords": keywords},
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json()
        return {"success": False, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {"topic": "香港"}
    result = execute(data)
    print(json.dumps(result, ensure_ascii=False))
