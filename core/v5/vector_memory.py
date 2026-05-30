"""向量记忆系统 - 真语义搜索（使用 TF-IDF + 余弦相似度）"""

import hashlib
import json
import math
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter


class VectorMemory:
    """向量记忆 - 语义搜索"""
    
    def __init__(self, user_id: str, agent_name: str):
        self.user_id = user_id
        self.agent_name = agent_name
        self.base_path = Path(f"{config_helper.get_data_root()}/v5/users/{user_id}/vectors/{agent_name}")
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.documents: List[Dict] = []
        self.idf: Dict[str, float] = {}
        self._load()
    
    def _load(self):
        file_path = self.base_path / "documents.json"
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.documents = data.get('documents', [])
                    self.idf = data.get('idf', {})
            except:
                pass
    
    def _save(self):
        with open(self.base_path / "documents.json", 'w') as f:
            json.dump({
                'documents': self.documents,
                'idf': self.idf
            }, f, indent=2)
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        import re
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', text.lower())
        return words
    
    def _compute_tf(self, words: List[str]) -> Dict[str, float]:
        """计算 TF"""
        tf = Counter(words)
        total = len(words)
        return {w: c/total for w, c in tf.items()}
    
    def _compute_tfidf(self, words: List[str]) -> List[float]:
        """计算 TF-IDF 向量"""
        tf = self._compute_tf(words)
        vec = []
        for word in set(words):
            if word in self.idf:
                vec.append(tf.get(word, 0) * self.idf[word])
            else:
                vec.append(tf.get(word, 0))
        return vec
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """余弦相似度"""
        if not vec1 or not vec2:
            return 0
        dot = sum(a*b for a,b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a*a for a in vec1))
        norm2 = math.sqrt(sum(b*b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0
        return dot / (norm1 * norm2)
    
    def add(self, text: str, metadata: Dict = None):
        """添加文档"""
        doc_id = hashlib.md5(f"{text}{time.time()}".encode()).hexdigest()[:8]
        words = self._tokenize(text)

        # 更新 IDF
        for w in set(words):
            self.idf[w] = self.idf.get(w, 0) + 1

        self.documents.append({
            "id": doc_id,
            "text": text,
            "words": words,
            "metadata": metadata or {},
            "timestamp": time.time()
        })

        # 限制文档数
        if len(self.documents) > 500:
            self.documents = self.documents[-500:]

        self._save()
    
    def search(self, query: str, limit: int = 3) -> List[Dict]:
        """语义搜索"""
        query_words = self._tokenize(query)
        query_vec = self._compute_tfidf(query_words)

        results = []
        for doc in self.documents:
            doc_vec = self._compute_tfidf(doc['words'])
            score = self._cosine_similarity(query_vec, doc_vec)
            results.append((score, doc))

        results.sort(key=lambda x: x[0], reverse=True)
        return [{"text": r[1]['text'], "score": round(r[0], 3), "metadata": r[1]['metadata']} 
                for r in results[:limit] if r[0] > 0.1]
    
    def get_stats(self) -> Dict:
        return {"total": len(self.documents), "vocab_size": len(self.idf)}


import time
