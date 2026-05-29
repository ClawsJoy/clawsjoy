from lib.smart_config import smart_config
"""向量记忆 - 使用 ChromaDB 语义搜索"""
import os
import chromadb
from chromadb.config import Settings
from pathlib import Path
import hashlib
from datetime import datetime

class VectorMemory:
    def __init__(self, persist_dir="data/vector_kb", collection_name="memory_vectors"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # 新版 ChromaDB 客户端
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        print(f"✅ 向量记忆初始化成功，集合大小: {self.collection.count()}")

    def add(self, text: str, category: str = "general", metadata: dict = None):
        doc_id = hashlib.md5(f"{text}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        meta = metadata or {}
        meta["category"] = category
        meta["timestamp"] = datetime.now().isoformat()
        
        self.collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[meta]
        )
        return doc_id

    def search(self, query: str, category: str = None, n: int = 5):
        where = {"category": category} if category else None
        results = self.collection.query(
            query_texts=[query],
            n_results=n,
            where=where
        )
        
        documents = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0]
        
        items = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            items.append({
                "text": doc,
                "metadata": meta,
                "similarity": 1 - dist
            })
        return items

    def get_stats(self):
        return {"total_vectors": self.collection.count(), "initialized": True}

    def list_all(self, limit=50):
        """列出所有向量"""
        results = self.collection.get(limit=limit)
        items = []
        for doc, meta in zip(results.get('documents', []), results.get('metadatas', [])):
            items.append({
                "text": doc[:100],
                "category": meta.get('category') if meta else 'unknown'
            })
        return items

vector_memory = VectorMemory()
