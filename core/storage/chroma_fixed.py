"""修复版 ChromaDB - 使用官方 OllamaEmbeddingFunction"""

import chromadb
from pathlib import Path
from typing import List, Dict, Optional
import uuid
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction as OfficialOllama


class ChromaFixed:
    def __init__(self, user_id: str, collection_name: str = "memories"):
        self.user_id = user_id
        self.collection_name = collection_name
        self.persist_dir = Path(f"{config_helper.get_data_root()}/chroma/{user_id}")
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(self.persist_dir))

        # 使用官方 embedding 函数
        self.embedding_fn = OfficialOllama(
            url=config_helper.get_llm_endpoint(),
            model_name=config_helper.get_embedding_model()
        )

        # 获取或创建 collection
        try:
            self.collection = self.client.get_collection(collection_name)
            print(f"   ✅ 使用已有 collection: {user_id}/{collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"   ✅ 创建新 collection: {user_id}/{collection_name}")

    def add(self, text: str, metadata: Dict = None) -> str:
        doc_id = str(uuid.uuid4())
        if metadata is None or metadata == {}:
            metadata = {"source": "user_preference", "timestamp": str(__import__('time').time())}

        self.collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata]
        )
        print(f"   ✅ 添加成功: {text[:50]}...")
        return doc_id

    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )

            formatted = []
            if results.get('documents') and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    distance = results['distances'][0][i] if results.get('distances') else 0
                    similarity = 1 / (1 + distance) if distance > 0 else 1.0
                    formatted.append({
                        'text': doc,
                        'similarity': similarity,
                        'metadata': results['metadatas'][0][i] if results.get('metadatas') else {}
                    })
            return formatted
        except Exception as e:
            print(f"   ⚠️ 搜索错误: {e}")
            return []

    def get_all(self) -> List[Dict]:
        try:
            results = self.collection.get()
            formatted = []
            if results.get('documents'):
                for i, doc in enumerate(results['documents']):
                    formatted.append({
                        'id': results['ids'][i],
                        'text': doc,
                        'metadata': results['metadatas'][i] if results.get('metadatas') else {}
                    })
            return formatted
        except Exception as e:
            print(f"   ⚠️ 获取失败: {e}")
            return []
