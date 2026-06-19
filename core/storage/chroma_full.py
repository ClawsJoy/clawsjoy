#!/usr/bin/env python3
"""Chroma Full - ChromaDB 向量存储（复用 vector_knowledge_center）"""

import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from core.lib.vector_knowledge_center import vector_knowledge_center
from core.lib.config_helper import get_data_root


class ChromaStore:
    """ChromaDB 向量存储 - 复用 vector_knowledge_center"""

    def __init__(self, user_id: str = "default", collection_name: str = "memories"):
        self.user_id = user_id
        self.persist_dir = Path(f"{get_data_root()}/chroma/{user_id}")
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # ✅ 复用 vector_knowledge_center 的 client
        self.client = vector_knowledge_center.client

        # ✅ 使用 ChromaDB 原生 embedding 函数
        from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
        self.embedding_fn = OllamaEmbeddingFunction(
            url="http://localhost:11434",
            model_name="nomic-embed-text"
        )

        # 尝试获取已有 collection，不存在则创建
        try:
            self.collection = self.client.get_collection(collection_name)
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_fn
            )

        print(f"   ✅ ChromaDB 已初始化: {user_id}/{collection_name}")

    def add(self, text: str, metadata: Dict = None) -> str:
        doc_id = str(uuid.uuid4())[:8]
        if metadata is None or len(metadata) == 0:
            metadata = {"source": "user", "timestamp": str(time.time())}

        self.collection.add(ids=[doc_id], documents=[text], metadatas=[metadata])
        return doc_id

    def search(self, query: str, limit: int = 3) -> List[Dict]:
        try:
            results = self.collection.query(query_texts=[query], n_results=limit)

            documents = []
            if results.get("ids") and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    doc = results["documents"][0][i] if results.get("documents") else ""
                    metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                    distance = results["distances"][0][i] if results.get("distances") else 0
                    similarity = 1 - distance

                    documents.append({
                        "id": doc_id,
                        "text": doc,
                        "similarity": round(similarity, 4),
                        "metadata": metadata,
                    })
            return documents
        except Exception as e:
            print(f"搜索错误: {e}")
            return []

    def get_count(self) -> int:
        return self.collection.count()


# 全局实例
chroma_store = ChromaStore()
