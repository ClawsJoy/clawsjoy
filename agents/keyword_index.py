#!/usr/bin/env python3
"""自研关键词索引引擎 - 不依赖 Meilisearch"""

import json
import re
from pathlib import Path
from collections import defaultdict

class KeywordIndex:
    def __init__(self, tenant_id="tenant_1"):
        self.tenant_id = tenant_id
        self.keywords_file = Path("/mnt/d/clawsjoy/data/keywords.json")
        self.index_file = Path("/mnt/d/clawsjoy/data/keyword_index.json")
        self._init_index()
    
    def _init_index(self):
        """初始化索引"""
        if not self.index_file.exists():
            self._build_index()
        else:
            with open(self.index_file) as f:
                self.index = json.load(f)
    
    def _build_index(self):
        """从 keywords.json 构建索引"""
        self.index = {"keywords": {}, "categories": defaultdict(list), "pinyin": {}}
        
        if not self.keywords_file.exists():
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
            return
        
        with open(self.keywords_file) as f:
            data = json.load(f)
        
        for cat, info in data.get("categories", {}).items():
            for kw in info.get("keywords", []):
                name = kw.get("name", kw) if isinstance(kw, dict) else kw
                if name:
                    # 主索引
                    self.index["keywords"][name] = {
                        "name": name,
                        "category": cat,
                        "slug": kw.get("slug", name) if isinstance(kw, dict) else name,
                        "weight": info.get("weight", 1.0)
                    }
                    # 分类索引
                    self.index["categories"][cat].append(name)
                    # 拼音简化（简单版）
                    self.index["pinyin"][name] = self._to_pinyin_simple(name)
        
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def _to_pinyin_simple(self, text):
        """简单拼音转换"""
        pinyin_map = {
            "香港": "xianggang", "深圳": "shenzhen", "上海": "shanghai",
            "北京": "beijing", "广州": "guangzhou", "优才": "youcai",
            "高才": "gaocai", "留学": "liuxue", "科技": "keji"
        }
        return pinyin_map.get(text, text.lower())
    
    def search(self, query, limit=5):
        """搜索关键词（支持模糊匹配）"""
        query_lower = query.lower()
        results = []
        
        for name, info in self.index["keywords"].items():
            score = 0
            # 完全匹配
            if query == name:
                score = 100
            # 包含匹配
            elif query in name:
                score = 80
            elif name in query:
                score = 60
            # 拼音匹配
            elif query in self.index["pinyin"].get(name, ""):
                score = 50
            # 分类匹配
            elif query in info["category"]:
                score = 30
            
            if score > 0:
                results.append({"name": name, "score": score, "category": info["category"]})
        
        # 按得分排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def add_keyword(self, name, category="通用", slug=None):
        """添加关键词到索引"""
        if name in self.index["keywords"]:
            return False
        
        self.index["keywords"][name] = {
            "name": name,
            "category": category,
            "slug": slug or name,
            "weight": 1.0
        }
        self.index["categories"].setdefault(category, []).append(name)
        self.index["pinyin"][name] = self._to_pinyin_simple(name)
        
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
        
        # 同步到 keywords.json
        self._sync_to_keywords_json(name, category, slug)
        return True
    
    def _sync_to_keywords_json(self, name, category, slug):
        """同步到 keywords.json"""
        with open(self.keywords_file) as f:
            data = json.load(f)
        
        if category not in data["categories"]:
            data["categories"][category] = {"keywords": [], "weight": 1.0}
        
        # 检查是否已存在
        exists = False
        for kw in data["categories"][category]["keywords"]:
            if kw.get("name", kw) == name:
                exists = True
                break
        
        if not exists:
            data["categories"][category]["keywords"].append({"name": name, "slug": slug or name})
            with open(self.keywords_file, 'w') as f:
                json.dump(data, f, indent=2)
    
    def get_stats(self):
        """获取索引统计"""
        return {
            "total_keywords": len(self.index["keywords"]),
            "categories": {cat: len(kws) for cat, kws in self.index["categories"].items()}
        }
    
    def rebuild(self):
        """重建索引"""
        self._build_index()

# 测试
if __name__ == "__main__":
    idx = KeywordIndex()
    print("=== 自研关键词索引 ===")
    print(f"统计: {idx.get_stats()}")
    
    # 搜索测试
    for q in ["优才", "香港", "留学", "科技", "移民"]:
        results = idx.search(q)
        print(f"\n搜索 '{q}': {[r['name'] for r in results]}")
    
    # 添加新词
    idx.add_keyword("人工智能", "科技")
    print(f"\n添加后统计: {idx.get_stats()}")
    print(f"搜索 '人工智能': {[r['name'] for r in idx.search('人工智能')]}")
