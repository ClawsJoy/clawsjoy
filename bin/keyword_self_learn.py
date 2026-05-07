#!/usr/bin/env python3
"""独立关键词学习进程"""

import time
import re
from pathlib import Path
import sys
sys.path.insert(0, '/mnt/d/clawsjoy/agents')
from keyword_learner import KeywordLearner

def learn_from_logs():
    learner = KeywordLearner()
    log_file = Path("/mnt/d/clawsjoy/logs/chat-api-out.log")
    
    if not log_file.exists():
        return
    
    with open(log_file) as f:
        logs = f.read()[-10000:]
    
    # 提取用户输入
    matches = re.findall(r'📥 处理: (.*?)\n', logs)
    new_candidates = []
    
    for match in matches[-30:]:
        words = re.findall(r'[\u4e00-\u9fa5]{2,4}', match)
        for w in words:
            if len(w) >= 2:
                new_candidates.append(w)
    
    new_candidates = list(set(new_candidates))
    if new_candidates:
        for w in new_candidates[:10]:
            learner.extract_candidates(w, "self_learn")
        learned = learner.auto_learn()
        if learned:
            print(f"📚 新学习: {learned}")

if __name__ == "__main__":
    while True:
        try:
            learn_from_logs()
        except Exception as e:
            print(f"错误: {e}")
        time.sleep(1800)  # 30分钟
