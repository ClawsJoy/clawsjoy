#!/usr/bin/env python3
"""记忆 Agent 学习 - 学习用户偏好和模式"""

import time
import json
from pathlib import Path

def learn_preferences():
    memory_file = Path("/mnt/d/clawsjoy/tenants/tenant_1/memory.json")
    if not memory_file.exists():
        return
    
    with open(memory_file) as f:
        memories = json.load(f)
    
    # 分析用户偏好
    preferences = {}
    for m in memories[-100:]:
        text = m.get("text", "")
        if "喜欢" in text or "偏好" in text:
            print(f"📝 记忆学习: 发现偏好模式")
    
    print(f"📚 记忆统计: {len(memories)} 条记忆")

if __name__ == "__main__":
    while True:
        learn_preferences()
        time.sleep(1800)  # 30分钟学习一次
