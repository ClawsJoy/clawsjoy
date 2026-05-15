import json
from pathlib import Path
import hashlib
from datetime import datetime

class SimpleMemory:
    def __init__(self, persist_file="data/memory_simple.json"):
        self.persist_file = Path(persist_file)
        self.persist_file.parent.mkdir(parents=True, exist_ok=True)
        self.memories = self._load()
    
    def _load(self):
        if self.persist_file.exists():
            with open(self.persist_file, 'r') as f:
                return json.load(f)
        return {"items": [], "categories": {}}
    
    def _save(self):
        with open(self.persist_file, 'w') as f:
            json.dump(self.memories, f, indent=2, ensure_ascii=False)
    
    def remember(self, fact, category="general"):
        doc_id = hashlib.md5(fact.encode()).hexdigest()
        item = {
            "id": doc_id,
            "fact": fact,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }
        existing_ids = [i["id"] for i in self.memories["items"]]
        if doc_id not in existing_ids:
            self.memories["items"].append(item)
        
        if category not in self.memories["categories"]:
            self.memories["categories"][category] = []
        if fact not in self.memories["categories"][category]:
            self.memories["categories"][category].append(fact)
        
        self._save()
        return True
    
    def recall(self, query, category=None, n=5):
        query_lower = query.lower()
        results = []
        
        items = self.memories["items"]
        if category:
            items = [i for i in items if i["category"] == category]
        
        for item in items:
            if query_lower in item["fact"].lower():
                results.append(item["fact"])
        
        return results[:n]
    
    def get_all(self, category=None):
        if category:
            return self.memories["categories"].get(category, [])
        return [i["fact"] for i in self.memories["items"]]
    
    def recall_all(self, category=None):
        """返回所有记忆（无数量限制）"""
        if category:
            return self.memories["categories"].get(category, [])
        return [i["fact"] for i in self.memories["items"]]
    
    def clear_category(self, goal, category):
        prefix = f"目标：{goal}"
        self.memories["items"] = [
            item for item in self.memories["items"]
            if not (item["fact"].startswith(prefix) and item["category"] == category)
        ]
        if category in self.memories["categories"]:
            self.memories["categories"][category] = []
        self._save()

memory = SimpleMemory()
