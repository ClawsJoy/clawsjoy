"""新版 ChromaDB 存储 - 符合 0.4.16+ 接口"""

import chromadb
from pathlib import Path
from typing import List, Dict, Optional
import uuid
from core.embedding_v2 import OllamaEmbeddingFunctionV2


class ChromaStoreV2:
    """新版 ChromaDB 向量存储"""
    
    def __init__(self, user_id: str, collection_name: str = "memories"):
        self.user_id = user_id
        self.persist_dir = Path(f"{config_helper.get_data_root()}/chroma/{user_id}")
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化客户端
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        
        # 使用新版 embedding
        self.embedding_fn = OllamaEmbeddingFunctionV2()
        
        # 获取或创建 collection（直接使用 get_or_create_collection）
        # 新版接口会自动处理 embedding 函数
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )
        
        print(f"   ✅ ChromaDB 已初始化: {user_id}/{collection_name}")
    
    def add(self, text: str, metadata: Dict = None) -> str:
        doc_id = str(uuid.uuid4())
        self.collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata or {}]
        )
        return doc_id
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
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
        except Exception as e:
            print(f"搜索错误: {e}")
            return []
    
    def delete_all(self):
        try:
            # 删除整个 collection 重建
            self.client.delete_collection(self.collection.name)
            self.collection = self.client.create_collection(
                name=self.collection.name,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )
        except:
            pass
    
    def get_count(self) -> int:
        return self.collection.count()


chroma_store = ChromaStoreV2
