#!/usr/bin/env python3
"""简单向量引擎"""

import json
import numpy as np
from pathlib import Path
import hashlib
import re
from datetime import datetime

class SimpleVectorEngine:
    def __init__(self):
        self.corpus_file = Path("/mnt/d/clawsjoy/data/simple_vector.json")
        self.documents = []
        self.word_index = {}
        self.doc_vectors = []
        self._load()
    
    def _load(self):
        if self.corpus_file.exists():
            try:
                with open(self.corpus_file) as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    self.word_index = data.get("word_index", {})
                    self.doc_vectors = data.get("doc_vectors", [])
            except:
                pass
    
    def _save(self):
        data = {
            "documents": self.documents,
            "word_index": self.word_index,
            "doc_vectors": self.doc_vectors
        }
        with open(self.corpus_file, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _tokenize(self, text: str):
        return re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text.lower())
    
    def add(self, text: str, metadata: dict = None):
        doc_id = hashlib.md5(f"{text}{datetime.now()}".encode()).hexdigest()[:12]
        words = self._tokenize(text)
        for w in words:
            if w not in self.word_index:
                self.word_index[w] = len(self.word_index)
        self.documents.append({
            "id": doc_id,
            "text": text,
            "metadata": metadata or {},
            "added_at": datetime.now().isoformat()
        })
        self._save()
        return doc_id
    
    def search(self, query: str, top_k: int = 5):
        return []
    
    def get_stats(self):
        return {"total_documents": len(self.documents), "vocab_size": len(self.word_index)}

simple_vector = SimpleVectorEngine()
