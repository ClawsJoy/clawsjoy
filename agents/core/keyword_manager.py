#!/usr/bin/env python3
"""关键词自管理系统 - Agent 自己学习、更新、优化关键词"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

class KeywordManager:
    def __init__(self):
        self.keyword_file = Path("data/keywords.json")
        self.load_keywords()
    
    def load_keywords(self):
        if self.keyword_file.exists():
            with open(self.keyword_file) as f:
                self.data = json.load(f)
        else:
            self.data = {
                "categories": {
                    "移民": {"keywords": ["优才", "高才", "专才", "移民", "签证", "身份"], "weight": 1.0},
                    "教育": {"keywords": ["留学", "大学", "申请", "学位", "教育"], "weight": 1.0},
                    "工作": {"keywords": ["就业", "招聘", "工作", "薪资", "行业"], "weight": 1.0},
                    "生活": {"keywords": ["租房", "美食", "购物", "交通", "生活"], "weight": 1.0},
                    "医疗": {"keywords": ["看病", "医院", "保险", "健康", "医疗"], "weight": 1.0}
                },
                "history": [],
                "stats": {"total_queries": 0, "learned": 0}
            }
        self.save()
    
    def save(self):
        with open(self.keyword_file, 'w') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def extract_keywords(self, text):
        """从文本中提取新关键词"""
        # 简单提取：2-6个中文字符的连续词
        candidates = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
        return [c for c in candidates if c not in self.get_all_keywords()]
    
    def get_all_keywords(self):
        """获取所有已知关键词"""
        all_kw = []
        for cat in self.data["categories"].values():
            all_kw.extend(cat["keywords"])
        return all_kw
    
    def learn_from_query(self, query, category_guess=None):
        """从用户查询中学习新词"""
        self.data["stats"]["total_queries"] += 1
        new_keywords = self.extract_keywords(query)
        
        learned = []
        for kw in new_keywords:
            # 确定分类
            cat = category_guess or self.guess_category(kw)
            if kw not in self.data["categories"][cat]["keywords"]:
                self.data["categories"][cat]["keywords"].append(kw)
                learned.append({"keyword": kw, "category": cat, "learned_at": datetime.now().isoformat()})
                self.data["stats"]["learned"] += 1
        
        if learned:
            self.data["history"].extend(learned)
            self.save()
            print(f"📚 学习了新关键词: {[l['keyword'] for l in learned]}")
        
        return learned
    
    def guess_category(self, keyword):
        """猜测关键词所属分类"""
        for cat, info in self.data["categories"].items():
            if any(k in keyword for k in info["keywords"]):
                return cat
        return "生活"  # 默认
    
    def optimize(self):
        """优化关键词（移除低频、合并相似）"""
        # 统计使用频率
        all_used = []
        for hist in self.data["history"]:
            all_used.append(hist["keyword"])
        
        counter = Counter(all_used)
        
        # 移除从未使用的关键词
        for cat in self.data["categories"].values():
            before = len(cat["keywords"])
            cat["keywords"] = [k for k in cat["keywords"] if k in counter or counter.get(k, 0) > 0]
            after = len(cat["keywords"])
            if before != after:
                print(f"优化 {cat}: 移除 {before - after} 个低频词")
        
        self.save()
    
    def suggest_for_input(self, user_input):
        """根据输入推荐分类和关键词"""
        matched = []
        for cat, info in self.data["categories"].items():
            for kw in info["keywords"]:
                if kw in user_input:
                    matched.append({"category": cat, "matched": kw, "weight": info["weight"]})
        
        if matched:
            # 按权重排序
            matched.sort(key=lambda x: x["weight"], reverse=True)
            return matched[0]["category"]
        return "生活"

if __name__ == "__main__":
    km = KeywordManager()
    
    # 模拟用户查询学习
    km.learn_from_query("香港高才通计划怎么申请", "移民")
    km.learn_from_query("香港优才计划最新政策", "移民")
    km.learn_from_query("上海落户条件2026", "移民")
    km.learn_from_query("深圳留学生补贴", "教育")
    
    print("\n当前关键词库:")
    print(json.dumps(km.data["categories"], ensure_ascii=False, indent=2))
    
    # 优化
    km.optimize()
    
    # 测试推荐
    test_input = "香港高才通怎么弄"
    print(f"\n输入: {test_input}")
    print(f"推荐分类: {km.suggest_for_input(test_input)}")
