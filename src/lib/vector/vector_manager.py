#!/usr/bin/env python3
"""Vector Manager - Vector Manager 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""统一向量管理器 - 修复版"""
import os
import pickle
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
from datetime import datetime

class VectorManager:
    def __init__(self, base_dir="data/vectors"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.vectors_file = self.base_dir / "vectors.json"
        self.metadata_file = self.base_dir / "metadata.json"
        
        self._load()
    
    def _load(self):
        """加载数据"""
        if self.vectors_file.exists():
            with open(self.vectors_file, 'r') as f:
                self.vectors = json.load(f)
        else:
            self.vectors = {}
        
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
        
        print(f"📚 加载向量库: {len(self.vectors)} 条")
    
    def _save(self):
        """保存数据"""
        with open(self.vectors_file, 'w') as f:
            json.dump(self.vectors, f, indent=2, ensure_ascii=False)
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def _get_embedding(self, text: str) -> List[float]:
        """获取简单向量（使用哈希）"""
        import hashlib
        # 简单但稳定的哈希向量
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()[:64]
        return [float(b) / 255.0 for b in hash_bytes]
    
    def add_knowledge(self, text: str, category: str, metadata: Dict = None):
        """添加知识"""
        vector = self._get_embedding(text)
        doc_id = hashlib.md5(f"{category}:{text[:50]}".encode()).hexdigest()[:16]
        
        self.vectors[doc_id] = vector
        self.metadata[doc_id] = {
            "text": text,
            "category": category,
            "type": "knowledge",
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        self._save()
        
        print(f"📚 添加知识 [{category}]: {text[:50]}...")
        return doc_id
    
    def add_memory(self, text: str, memory_type: str, importance: float = 0.5):
        """添加记忆"""
        vector = self._get_embedding(text)
        doc_id = hashlib.md5(f"mem:{memory_type}:{text[:50]}".encode()).hexdigest()[:16]
        
        self.vectors[doc_id] = vector
        self.metadata[doc_id] = {
            "text": text,
            "type": "memory",
            "memory_type": memory_type,
            "importance": importance,
            "timestamp": datetime.now().isoformat()
        }
        self._save()
        
        print(f"💭 添加记忆 [{memory_type}]: {text[:50]}...")
        return doc_id
    
    def search(self, query: str, top_k: int = 5, category: str = None) -> List[Dict]:
        """向量检索"""
        query_vec = self._get_embedding(query)
        
        results = []
        for doc_id, vec in self.vectors.items():
            meta = self.metadata.get(doc_id, {})
            if category and meta.get("category") != category:
                continue
            
            # 简单匹配（直接包含查询词）
            query_words = query.lower().split()
            text_lower = meta.get("text", "").lower()
            
            score = 0
            for word in query_words:
                if word in text_lower:
                    score += 1
            
            if score > 0:
                results.append({
                    "id": doc_id,
                    "text": meta.get("text", ""),
                    "similarity": score / max(len(query_words), 1),
                    "metadata": meta
                })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def get_stats(self):
        return {
            "total_vectors": len(self.vectors),
            "knowledge_count": len([m for m in self.metadata.values() if m.get("type") == "knowledge"]),
            "memory_count": len([m for m in self.metadata.values() if m.get("type") == "memory"])
        }

vector_manager = VectorManager()
