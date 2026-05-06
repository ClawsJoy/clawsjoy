#!/usr/bin/env python3
"""话题规划器 - 从扩展库中选择话题"""

import json
import random
from pathlib import Path
from datetime import datetime

TOPICS_FILE = Path("/mnt/d/clawsjoy/topics_library.json")
HISTORY_FILE = Path("/mnt/d/clawsjoy/output/topics/history.json")

def load_topics():
    with open(TOPICS_FILE, 'r') as f:
        return json.load(f)

def get_topic_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_topic_history(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history[-100:], f, ensure_ascii=False, indent=2)

def select_topic(category=None, avoid_recent=3):
    """选择话题，避免重复"""
    topics = load_topics()
    history = get_topic_history()
    recent_topics = [h['topic'] for h in history[-avoid_recent:]]
    
    if category and category in topics:
        candidates = topics[category]
    else:
        candidates = []
        for cat_items in topics.values():
            candidates.extend(cat_items)
    
    # 过滤近期话题
    available = [t for t in candidates if t['topic'] not in recent_topics]
    
    if not available:
        available = candidates
    
    selected = random.choice(available)
    
    # 记录
    history.append({
        "topic": selected['topic'],
        "category": selected['category'],
        "selected_at": datetime.now().isoformat()
    })
    save_topic_history(history)
    
    return selected

if __name__ == "__main__":
    import sys
    category = sys.argv[1] if len(sys.argv) > 1 else None
    result = select_topic(category)
    print(json.dumps(result, ensure_ascii=False, indent=2))
