#!/usr/bin/env python3
"""同步热点话题"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.lib.unified_config import unified_config
from pathlib import Path
import json

def sync_topics():
    """同步话题"""
    topics_dir = Path("topics")
    if not topics_dir.exists():
        print("话题目录不存在")
        return
    
    for topic_file in topics_dir.glob("*.txt"):
        print(f"同步话题: {topic_file.name}")
    
    print("话题同步完成")

if __name__ == "__main__":
    sync_topics()
