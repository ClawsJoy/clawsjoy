#!/usr/bin/env python3
"""关键词学习器专属学习 - 语义知识"""

import json
import re
from pathlib import Path
from base_learner import BaseLearner

class KeywordLearnerV2(BaseLearner):
    def __init__(self):
        super().__init__("keyword_learner", "semantic")
        self.keywords_file = Path("/mnt/d/clawsjoy/data/keywords.json")
    
    def learn(self, user_input=None):
        """从用户输入学习新关键词"""
        if not user_input:
            return []
        
        # 提取候选词
        candidates = re.findall(r'[\u4e00-\u9fa5]{2,4}', user_input)
        candidates += re.findall(r'[a-zA-Z]{3,8}', user_input)
        
        # 过滤停用词
        stopwords = {'我们', '他们', '这个', '那个', '可以', '已经', '还是'}
        candidates = [c for c in candidates if c not in stopwords]
        
        # 与已有知识对比
        existing = self._get_existing_keywords()
        new_words = [c for c in candidates if c not in existing]
        
        if new_words:
            self.learned["knowledge"].extend([
                {"word": w, "learned_at": __import__('time').time(), "source": "user"}
                for w in new_words
            ])
            self.save_learned()
        
        return new_words
    
    def _get_existing_keywords(self):
        existing = set()
        if self.keywords_file.exists():
            with open(self.keywords_file) as f:
                data = json.load(f)
            for cat, info in data.get("categories", {}).items():
                for kw in info.get("keywords", []):
                    name = kw.get("name", kw) if isinstance(kw, dict) else kw
                    existing.add(name)
        return existing
    
    def suggest_category(self, keyword):
        """建议关键词分类"""
        category_map = {
            "移民": ["优才", "高才", "人才", "签证", "永居", "身份"],
            "科技": ["AI", "人工智能", "芯片", "算法", "数据"],
            "教育": ["留学", "大学", "申请", "学位", "考研"]
        }
        for cat, keywords in category_map.items():
            for kw in keywords:
                if kw in keyword or keyword in kw:
                    return cat
        return "通用"
    
    def get_stats(self):
        stats = super().get_stats()
        stats["total_keywords"] = len(self._get_existing_keywords())
        return stats

if __name__ == "__main__":
    learner = KeywordLearnerV2()
    new = learner.learn("我喜欢人工智能和机器学习")
    print(f"新词: {new}")
    print(f"建议分类: {learner.suggest_category('人工智能')}")
    print(f"统计: {learner.get_stats()}")
