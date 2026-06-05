#!/usr/bin/env python3
"""Chroma Store Optimized - Chroma Store Optimized 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


import uuid
from pathlib import Path
from typing import Dict, List, Optional

import chromadb
import numpy as np
from chromadb.utils import embedding_functions

from core.lib.unified_config import unified_config


class ChromaStoreOptimized:
    """优化版 ChromaDB 向量存储"""

    def __init__(self, user_id: str, collection_name: str = "memories"):
        self.user_id = user_id
        self.persist_dir = Path(f"{config_helper.get_data_root()}/chroma/{user_id}")
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # 初始化客户端
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))

        # 使用 Ollama embedding（本地，高质量）
        self.embedding_fn = embedding_functions.OllamaEmbeddingFunction(
            model_name=config_helper.get_embedding_model(),
            url="http://localhost:11434/api/embeddings",
        )

        # 获取或创建 collection，使用余弦距离
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},  # 使用余弦相似度
        )

        print(f"   ✅ ChromaDB 已优化: {user_id}/{collection_name}")

    def add(self, text: str, metadata: Dict = None) -> str:
        """添加文档"""
        doc_id = str(uuid.uuid4())

        # 添加更多元数据以便过滤
        meta = metadata or {}
        meta["timestamp"] = __import__("time").time()
        meta["text_length"] = len(text)

        self.collection.add(ids=[doc_id], documents=[text], metadatas=[meta])
        return doc_id

    def add_batch(self, texts: List[str], metadatas: List[Dict] = None) -> List[str]:
        """批量添加"""
        ids = [str(uuid.uuid4()) for _ in texts]
        if metadatas is None:
            metadatas = [{} for _ in texts]

        self.collection.add(ids=ids, documents=texts, metadatas=metadatas)
        return ids

    def search(
        self, query: str, limit: int = 5, filter_condition: Dict = None
    ) -> List[Dict]:
        """语义搜索 - 返回相似度分数"""
        try:
            # 执行查询
            results = self.collection.query(
                query_texts=[query], n_results=limit, where=filter_condition
            )

            documents = []
            if results["ids"] and results["ids"][0]:
                # 计算相似度分数（cosine 距离转相似度）
                for i, doc_id in enumerate(results["ids"][0]):
                    doc = results["documents"][0][i] if results["documents"] else ""
                    metadata = (
                        results["metadatas"][0][i] if results["metadatas"] else {}
                    )
                    distance = results["distances"][0][i] if results["distances"] else 0

                    # 余弦距离转相似度: similarity = 1 - distance
                    similarity = 1 - distance

                    documents.append(
                        {
                            "id": doc_id,
                            "text": doc,
                            "similarity": round(similarity, 4),
                            "metadata": metadata,
                        }
                    )

            return documents
        except Exception as e:
            print(f"搜索错误: {e}")
            return []

    def search_by_metadata(self, metadata_filter: Dict, limit: int = 10) -> List[Dict]:
        """按元数据过滤搜索"""
        try:
            results = self.collection.get(where=metadata_filter, limit=limit)

            documents = []
            if results["ids"]:
                for i, doc_id in enumerate(results["ids"]):
                    documents.append(
                        {
                            "id": doc_id,
                            "text": (
                                results["documents"][i] if results["documents"] else ""
                            ),
                            "metadata": (
                                results["metadatas"][i] if results["metadatas"] else {}
                            ),
                        }
                    )
            return documents
        except Exception as e:
            print(f"元数据搜索错误: {e}")
            return []

    def delete(self, doc_id: str):
        """删除文档"""
        try:
            self.collection.delete(ids=[doc_id])
        except Exception as e:
            print(f"删除错误: {e}")

    def get_count(self) -> int:
        return self.collection.count()

    def get_stats(self) -> Dict:
        return {
            "total": self.collection.count(),
            "collection_name": self.collection.name,
            "user_id": self.user_id,
        }


chroma_store = ChromaStoreOptimized
