#!/usr/bin/env python3
#!/usr/bin/env python3
"""Fix Memory Api - Fix Memory Api 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import requests
import json

def fix_memory_api():
    """修复记忆 API"""
    url = "http://localhost:5002/api/v5/memory/recall"
    try:
        response = requests.post(url, json={"user_id": "test"})
        print(f"响应: {response.status_code}")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    fix_memory_api()
