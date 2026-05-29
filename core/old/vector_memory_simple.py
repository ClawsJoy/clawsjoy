"""简化版向量记忆 - 稳定版本"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict
import uuid
import time
from core.lib.unified_config import unified_config


class VectorMemory:
    def __init__(self, user_id: str):
        self.user_id = user_id
        data_root = unified_config.get("paths.data_root", "data")
        self.base_path = Path(f"{data_root}/vector_memory/{user_id}")
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.file_path = self.base_path / "memories.json"
        self.documents = []
        self.embeddings = []
        self._load()

    def _load(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    self.documents = data.get('documents', [])
                    self.embeddings = [np.array(e) for e in data.get('embeddings', [])]
            except:
                pass

    def _save(self):
        data = {
            'documents': self.documents,
            'embeddings': [e.tolist() for e in self.embeddings]
        }
        with open(self.file_path, 'w') as f:
            json.dump(data, f)

    def _get_embedding(self, text: str):
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        return np.array([ord(c) / 255 for c in hash_obj.hexdigest()[:50]], dtype=np.float32)

    def add(self, text: str, metadata: dict = None):
        doc_id = str(uuid.uuid4())[:8]
        self.documents.append({
            'id': doc_id,
            'text': text,
            'metadata': metadata or {},
            'timestamp': time.time()
        })
        self.embeddings.append(self._get_embedding(text))
        if len(self.documents) > 200:
            self.documents = self.documents[-200:]
            self.embeddings = self.embeddings[-200:]
        self._save()

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        if not self.embeddings:
            return []
        query_vec = self._get_embedding(query)
        similarities = []
        for i, doc_vec in enumerate(self.embeddings):
            sim = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec) + 1e-8)
            similarities.append((sim, i))
        similarities.sort(reverse=True)
        results = []
        for sim, i in similarities[:limit]:
            results.append({
                'text': self.documents[i]['text'],
                'similarity': float(sim),
                'metadata': self.documents[i].get('metadata', {})
            })
        return results


def get_vector_memory(user_id: str):
    return VectorMemory(user_id)
