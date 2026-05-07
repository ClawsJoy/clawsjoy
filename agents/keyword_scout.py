#!/usr/bin/env python3
"""关键词采集特工 - 专门提取和扩展关键词"""

import re
import json
from pathlib import Path
from collections import Counter

class KeywordScout:
    def __init__(self):
        self.keyword_db = Path("data/keywords/collected.json")
        self.load()
    
    def load(self):
        if self.keyword_db.exists():
            with open(self.keyword_db) as f:
                self.keywords = json.load(f)
        else:
            self.keywords = {"移民": [], "教育": [], "工作": [], "生活": [], "医疗": []}
    
    def save(self):
        self.keyword_db.parent.mkdir(parents=True, exist_ok=True)
        with open(self.keyword_db, 'w') as f:
            json.dump(self.keywords, f, ensure_ascii=False, indent=2)
    
    def extract_from_text(self, text, category):
        """从文本中提取关键词"""
        # 提取2-6个中文字符
        candidates = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
        
        # 过滤停用词
        stopwords = ['我们', '他们', '这个', '那个', '可以', '进行', '已经', '还是']
        new_keywords = [c for c in candidates if c not in stopwords and len(c) >= 2]
        
        # 去重
        existing = set(self.keywords.get(category, []))
        added = []
        for kw in new_keywords[:20]:
            if kw not in existing:
                self.keywords[category].append(kw)
                added.append(kw)
        
        if added:
            print(f"📚 {category} 新增关键词: {added}")
            self.save()
        
        return added
    
    def suggest_by_category(self, category, limit=10):
        """获取某分类的热门关键词"""
        return self.keywords.get(category, [])[:limit]

if __name__ == "__main__":
    scout = KeywordScout()
    scout.extract_from_text("香港优才计划、高才通、专才计划", "移民")
    print(f"移民类关键词: {scout.suggest_by_category('移民')}")
