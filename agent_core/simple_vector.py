#!/usr/bin/env python3
"""简单向量引擎 - 修复版"""

import json
import numpy as np
from pathlib import Path
import hashlib
import re
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SimpleVectorEngine:
    def __init__(self):
        self.corpus_file = Path("/mnt/d/clawsjoy/data/simple_vector.json")
        self.documents = []
        self.vectorizer = None
        self.matrix = None
        self._load()
    
    def _load(self):
        if self.corpus_file.exists():
            try:
                with open(self.corpus_file) as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    # 重建向量
                    if self.documents:
                        texts = [d.get("text", "") for d in self.documents]
                        self.vectorizer = TfidfVectorizer(max_features=500)
                        self.matrix = self.vectorizer.fit_transform(texts)
                print(f"📚 加载向量库: {len(self.documents)} 条")
            except Exception as e:
                print(f"加载失败: {e}")
                self.documents = []
        else:
            print("📚 初始化新向量库")
    
    def _save(self):
        data = {"documents": self.documents}
        with open(self.corpus_file, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add(self, text: str, metadata: dict = None):
        doc_id = hashlib.md5(f"{text}{datetime.now()}".encode()).hexdigest()[:12]
        self.documents.append({
            "id": doc_id,
            "text": text,
            "metadata": metadata or {},
            "added_at": datetime.now().isoformat()
        })
        # 重建向量
        texts = [d.get("text", "") for d in self.documents]
        self.vectorizer = TfidfVectorizer(max_features=500)
        self.matrix = self.vectorizer.fit_transform(texts)
        self._save()
        print(f"   📝 已添加: {text[:50]}...")
        return doc_id
    
    def search(self, query: str, top_k: int = 5):
        if not self.documents or self.vectorizer is None:
            return []
        try:
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.matrix)[0]
            # 获取 top_k 索引
            top_indices = np.argsort(similarities)[::-1][:top_k]
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:
                    results.append({
                        "score": float(similarities[idx]),
                        "text": self.documents[idx]["text"],
                        "metadata": self.documents[idx].get("metadata", {})
                    })
            return results
        except Exception as e:
            print(f"搜索错误: {e}")
            return []
    
    def get_stats(self):
        return {"total_documents": len(self.documents), "vocab_size": 500}

simple_vector = SimpleVectorEngine()
