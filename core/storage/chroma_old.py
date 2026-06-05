"""旧版系统 ChromaDB 向量存储 - 修复版"""

import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import chromadb

from core.embedding_fixed import OllamaEmbeddingFunction


class ChromaMemory:
    """为旧版系统提供的向量记忆"""

    def __init__(self, user_id: str, collection_name: str = "memories"):
        self.user_id = user_id
        self.persist_dir = Path(f"{config_helper.get_data_root()}/chroma/{user_id}")
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.embedding_fn = OllamaEmbeddingFunction()

        # 删除旧 collection 避免冲突
        try:
            self.client.delete_collection(collection_name)
        except Exception as e:
            pass

        self.collection = self.client.create_collection(
            name=collection_name, embedding_function=self.embedding_fn
        )

        print(f"   ✅ 向量记忆已启用: {user_id}")

    def add(self, text: str, metadata: Dict = None) -> str:
        doc_id = str(uuid.uuid4())[:8]
        if metadata is None or len(metadata) == 0:
            metadata = {"source": "butler", "timestamp": str(time.time())}

        self.collection.add(ids=[doc_id], documents=[text], metadatas=[metadata])
        return doc_id

    def search(self, query: str, limit: int = 3) -> List[Dict]:
        try:
            results = self.collection.query(query_texts=[query], n_results=limit)

            documents = []
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    doc = results["documents"][0][i] if results["documents"] else ""
                    metadata = (
                        results["metadatas"][0][i] if results["metadatas"] else {}
                    )
                    distance = results["distances"][0][i] if results["distances"] else 0
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
            print(f"   ⚠️ 向量搜索错误: {e}")
            return []

    def get_count(self) -> int:
        return self.collection.count()


# 便捷函数
def get_vector_memory(user_id: str) -> ChromaMemory:
    return ChromaMemory(user_id)
