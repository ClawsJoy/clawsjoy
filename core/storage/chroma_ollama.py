"""ChromaDB 存储 - 修复 metadata 问题"""

import chromadb
import requests
from pathlib import Path
from typing import List, Dict, Optional
import uuid


class OllamaEmbeddingFunction:
    """符合 ChromaDB 要求的 Embedding 函数"""
    
    def __init__(self):
        self.url = "http://localhost:11434/api/embeddings"
        self.model = config_helper.get_embedding_model()
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        embeddings = []
        for text in input:
            try:
                response = requests.post(
                    self.url,
                    json={"model": self.model, "prompt": text},
                    timeout=config_helper.get_timeout("default")
                )
                if response.status_code == 200:
                    embedding = response.json().get('embedding', [])
                    embeddings.append(embedding)
                else:
                    embeddings.append([0.0] * 768)
            except Exception as e:
                print(f"   ⚠️ Embedding 失败: {e}")
                embeddings.append([0.0] * 768)
        return embeddings


class ChromaOllama:
    def __init__(self, user_id: str, collection_name: str = "memories"):
        self.user_id = user_id
        self.persist_dir = Path(f"{config_helper.get_data_root()}/chroma/{user_id}")
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.embedding_fn = OllamaEmbeddingFunction()

        # 删除旧 collection
        try:
            self.client.delete_collection(collection_name)
        except:
            pass

        self.collection = self.client.create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

        print(f"   ✅ ChromaDB 已初始化: {user_id}/{collection_name}")
    
    def add(self, text: str, metadata: Dict = None) -> str:
        doc_id = str(uuid.uuid4())
        # 修复：metadata 不能为 None 或空字典，必须有内容
        if metadata is None:
            metadata = {"source": "user_input", "timestamp": str(__import__('time').time())}
        elif len(metadata) == 0:
            metadata = {"source": "user_input", "timestamp": str(__import__('time').time())}

        self.collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata]
        )
        return doc_id
    
    def search(self, query: str, limit: int = 3) -> List[Dict]:
        results = self.collection.query(query_texts=[query], n_results=limit)

        documents = []
        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                doc = results['documents'][0][i] if results['documents'] else ""
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 0
                similarity = 1 - distance
                
                documents.append({
                    "id": doc_id,
                    "text": doc,
                    "similarity": round(similarity, 4),
                    "metadata": metadata
                })
        return documents
    
    def get_count(self) -> int:
        return self.collection.count()


chroma_store = ChromaOllama
