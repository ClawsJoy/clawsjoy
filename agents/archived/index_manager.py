"""统一索引管理器 - 整合资料库、关键词、记忆"""

import json
import requests
from pathlib import Path
from .knowledge_base import KnowledgeBase

class IndexManager:
    def __init__(self, tenant_id="tenant_1"):
        self.tenant_id = tenant_id
        self.kb = KnowledgeBase(tenant_id)
        self.meilisearch = "http://localhost:7700"
        self.memory_file = Path(f"/mnt/d/clawsjoy/tenants/{tenant_id}/memory.json")
        self._init_memory()
    
    def _init_memory(self):
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.memory_file.exists():
            with open(self.memory_file, 'w') as f:
                json.dump([], f)
    
    # ========== 关键词索引 ==========
    def search_keywords(self, query, limit=5):
        """搜索关键词"""
        try:
            resp = requests.post(f"{self.meilisearch}/indexes/keywords/search",
                                json={"q": query, "limit": limit}, timeout=2)
            if resp.status_code == 200:
                return [h["name"] for h in resp.json().get("hits", [])]
        except:
            pass
        return []
    
    # ========== 资料库索引 ==========
    def search_knowledge(self, query, limit=3):
        """搜索资料库"""
        return self.kb.search(query, limit)
    
    # ========== 记忆索引 ==========
    def recall(self, query, limit=3):
        """回忆历史记忆"""
        with open(self.memory_file) as f:
            memories = json.load(f)
        # 简单匹配（可用向量搜索增强）
        matched = [m for m in memories if query in m.get("text", "")]
        return matched[-limit:] if matched else []
    
    def remember(self, text, type="interaction"):
        """记录记忆"""
        with open(self.memory_file) as f:
            memories = json.load(f)
        memories.append({"text": text, "type": type, "time": __import__("time").time()})
        # 只保留最近 100 条
        with open(self.memory_file, 'w') as f:
            json.dump(memories[-100:], f, indent=2)
    
    # ========== 智能检索 ==========
    def smart_search(self, query):
        """综合检索：关键词 + 资料库 + 记忆"""
        return {
            "keywords": self.search_keywords(query),
            "knowledge": self.search_knowledge(query),
            "memory": self.recall(query)
        }

def search_keywords(self, query, limit=5):
    """搜索关键词 - 修复版"""
    try:
        resp = requests.post(
            f"{self.meilisearch}/indexes/keywords/search",
            json={"q": query, "limit": limit},
            timeout=2
        )
        if resp.status_code == 200:
            hits = resp.json().get("hits", [])
            return [h.get("name") or h.get("id") for h in hits if h]
    except Exception as e:
        print(f"搜索失败: {e}")
    return []
