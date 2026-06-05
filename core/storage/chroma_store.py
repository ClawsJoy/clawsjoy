#!/usr/bin/env python3
"""Chroma Store - Chroma Store 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


import uuid
from pathlib import Path
from typing import Dict, List, Optional

import chromadb
from chromadb.utils import embedding_functions


class ChromaStore:
    """ChromaDB 向量存储"""

    def __init__(self, user_id: str, collection_name: str = "memories"):
        self.user_id = user_id
        self.persist_dir = Path(f"{config_helper.get_data_root()}/chroma/{user_id}")
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # 初始化客户端
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))

        # 使用默认 embedding 函数
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        # 获取或创建 collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=self.embedding_fn
        )

        print(f"   ✅ ChromaDB 已初始化: {user_id}/{collection_name}")

    def add(self, text: str, metadata: Dict = None) -> str:
        """添加文档"""
        doc_id = str(uuid.uuid4())
        self.collection.add(ids=[doc_id], documents=[text], metadatas=[metadata or {}])
        return doc_id

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """语义搜索"""
        results = self.collection.query(query_texts=[query], n_results=limit)

        documents = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                documents.append(
                    {
                        "text": doc,
                        "score": (
                            1 - results["distances"][0][i]
                            if results["distances"]
                            else 1.0
                        ),
                        "metadata": (
                            results["metadatas"][0][i] if results["metadatas"] else {}
                        ),
                    }
                )

        return documents

    def get_count(self) -> int:
        return self.collection.count()


chroma_store = ChromaStore
