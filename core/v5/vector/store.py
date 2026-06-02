#!/usr/bin/env python3
"""Store - Store 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class VectorDoc:
    """向量文档"""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict


class VectorStore:
    """向量存储"""
    
    def __init__(self, user_id: str, collection: str = "default"):
        self.user_id = user_id
        self.collection = collection
        self.base_path = Path(f"{config_helper.get_data_root()}/v5/users/{user_id}/vectors/{collection}")
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.documents: List[VectorDoc] = []
        self._load()
    
    def _load(self):
        """加载数据"""
        index_file = self.base_path / "index.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    self.documents.append(VectorDoc(**item))
    
    def _save(self):
        """保存数据"""
        with open(self.base_path / "index.json", 'w') as f:
            data = [{"id": d.id, "content": d.content, "embedding": d.embedding, "metadata": d.metadata} for d in self.documents]
            json.dump(data, f, indent=2)
    
    def _simple_embedding(self, text: str) -> List[float]:
        """简单 embedding（实际应使用模型）"""
        # 简化的 TF-IDF 风格
        words = text.lower().split()
        vec = [hash(w) % 100 / 100 for w in words[:50]]
        while len(vec) < 50:
            vec.append(0.0)
        return vec[:50]
    
    def add(self, content: str, metadata: Dict = None) -> str:
        """添加文档"""
        import uuid
        doc_id = str(uuid.uuid4())[:8]
        embedding = self._simple_embedding(content)

        self.documents.append(VectorDoc(
            id=doc_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {}
        ))

        if len(self.documents) > 1000:
            self.documents = self.documents[-1000:]

        self._save()
        return doc_id
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """语义搜索"""
        query_vec = self._simple_embedding(query)

        # 计算相似度
        scores = []
        for doc in self.documents:
            # 余弦相似度
            dot = sum(a * b for a, b in zip(query_vec, doc.embedding))
            norm_q = sum(a * a for a in query_vec) ** 0.5
            norm_d = sum(b * b for b in doc.embedding) ** 0.5
            sim = dot / (norm_q * norm_d + 1e-8)
            scores.append((sim, doc))

        scores.sort(key=lambda x: x[0], reverse=True)

        return [{"content": doc.content, "score": sim, "metadata": doc.metadata} for sim, doc in scores[:limit]]
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {"total_documents": len(self.documents)}


vector_store = VectorStore
