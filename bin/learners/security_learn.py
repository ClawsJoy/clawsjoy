#!/usr/bin/env python3
"""安全 Agent 学习 - 学习新的敏感信息模式"""

import time
import re
from pathlib import Path

def learn_new_patterns():
    patterns_file = Path("/mnt/d/clawsjoy/data/sensitive_patterns.json")
    log_file = Path("/mnt/d/clawsjoy/logs/chat-api-out.log")
    
    if not log_file.exists():
        return
    
    with open(log_file) as f:
        logs = f.read()
    
    # 提取可能的敏感信息模式
    potential_patterns = []
    
    # API Key 模式
    api_key_pattern = r'[a-zA-Z0-9]{32,40}'
    matches = re.findall(api_key_pattern, logs)
    if matches:
        potential_patterns.append({"type": "api_key", "pattern": api_key_pattern, "learned_at": time.time()})
    
    # Token 模式
    token_pattern = r'ya29\.[a-zA-Z0-9_-]+'
    if re.search(token_pattern, logs):
        potential_patterns.append({"type": "token", "pattern": token_pattern, "learned_at": time.time()})
    
    if potential_patterns:
        print(f"🔒 安全学习: 发现 {len(potential_patterns)} 个新模式")

if __name__ == "__main__":
    while True:
        learn_new_patterns()
        time.sleep(3600)  # 每小时学习一次
