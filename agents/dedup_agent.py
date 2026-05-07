#!/usr/bin/env python3
"""去重特工 - 检查内容重复"""

import hashlib
import json
from pathlib import Path

class DedupAgent:
    def __init__(self):
        self.index_file = Path("data/content/index.json")
        self.load()
    
    def load(self):
        if self.index_file.exists():
            with open(self.index_file) as f:
                self.index = json.load(f)
        else:
            self.index = {}
    
    def save(self):
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def get_hash(self, content):
        """计算内容哈希"""
        return hashlib.md5(content[:500].encode()).hexdigest()
    
    def is_duplicate(self, content):
        """检查是否重复"""
        h = self.get_hash(content)
        if h in self.index:
            return True, self.index[h]
        self.index[h] = {"count": 1, "first_seen": str(__import__('time').time())}
        self.save()
        return False, None

if __name__ == "__main__":
    dedup = DedupAgent()
    print(dedup.is_duplicate("香港优才计划2026"))  # 第一次
    print(dedup.is_duplicate("香港优才计划2026"))  # 第二次（重复）
