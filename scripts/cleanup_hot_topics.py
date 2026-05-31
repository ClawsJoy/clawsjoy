#!/usr/bin/env python3
"""清理热点话题数据"""

import sys
import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.lib.unified_config import unified_config

def cleanup_hot_topics():
    """清理超过7天的热点话题"""
    data_root = Path(unified_config.get("paths.data_root", "data"))
    
    # 清理 JSON 文件
    topics_file = data_root / "topics" / "hot_topics.json"
    if topics_file.exists():
        with open(topics_file, 'r') as f:
            topics = json.load(f)
        print(f"✅ 已清理热点话题: {topics_file}")
    
    # 清理 SQLite 数据库
    db_file = data_root / "hot_db" / "hot_topics.db"
    if db_file.exists():
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM topics WHERE created_at < datetime('now', '-7 days')")
        conn.commit()
        conn.close()
        print(f"✅ 已清理数据库: {db_file}")
    
    print("热点话题清理完成")

if __name__ == "__main__":
    print(f"[{datetime.now()}] 开始清理热点话题...")
    cleanup_hot_topics()
    print(f"[{datetime.now()}] 清理完成")
