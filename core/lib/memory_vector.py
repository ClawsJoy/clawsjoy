from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
"""向量记忆模块 - 修复版"""
import hashlib
import chromadb
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class VectorMemory:
    def __init__(self, persist_dir: str = f"{get_data_root()}/vector_kb"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection_name = "conversation"
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def add(self, text: str, category: str = "general", metadata: dict = None) -> str:
        """添加向量记忆"""
        doc_id = hashlib.md5(f"{text}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        meta = metadata or {}
        meta["category"] = category
        meta["timestamp"] = datetime.now().isoformat()
        meta["doc_id"] = doc_id
        
        self.collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[meta]
        )
        return doc_id

    def search(self, query: str, n: int = 5, category: str = None, where: dict = None) -> List[Dict]:
        """搜索向量记忆"""
        try:
            where_filter = {}
            if category:
                where_filter['category'] = category
            if where:
                where_filter.update(where)
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n,
                where=where_filter if where_filter else None
            )
            
            items = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    item = {
                        "text": doc,
                        "similarity": results['distances'][0][i] if results['distances'] else 0,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "id": results['ids'][0][i]
                    }
                    items.append(item)
            return items
        except Exception as e:
            print(f"搜索失败: {e}")
            return []

    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "total_vectors": self.collection.count(),
            "collection_name": self.collection_name,
            "initialized": True
        }


vector_memory = VectorMemory()
