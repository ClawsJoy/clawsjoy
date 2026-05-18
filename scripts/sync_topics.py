#!/usr/bin/env python3
"""定时同步话题到向量库"""
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
import json
from src.lib.vector.vector_manager import vector_manager

with open('data/topics/hot_topics.json', 'r') as f:
    data = json.load(f)

count = 0
for category, topics in data.items():
    for topic in topics:
        vector_manager.add_knowledge(
            f'热门话题: {topic} (分类:{category})',
            category='hot_topic',
            metadata={'topic': topic, 'category': category, 'source': 'local'}
        )
        count += 1

print(f'[{__import__("datetime").datetime.now()}] 已同步 {count} 条话题')
