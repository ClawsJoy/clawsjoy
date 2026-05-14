"""向量记忆系统 - 基于 ChromaDB 的语义检索"""
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional

class VectorMemory:
    """增强版记忆系统，支持向量检索"""
    
    def __init__(self, persist_dir="data/vector_memory"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._init_chromadb()
    
    def _init_chromadb(self):
        """初始化 ChromaDB"""
        try:
            import chromadb
            from chromadb.config import Settings
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(self.persist_dir),
                anonymized_telemetry=False
            ))
            self.collection = self.client.get_or_create_collection(
                name="clawsjoy_memory",
                metadata={"hnsw:space": "cosine"}
            )
            print("✅ 向量记忆系统已初始化")
        except Exception as e:
            print(f"⚠️ ChromaDB 初始化失败: {e}")
            self.client = None
            self.collection = None
    
    def add(self, text: str, metadata: Dict = None, category: str = "general"):
        """添加记忆"""
        if not self.collection:
            return False
        
        # 生成唯一 ID
        memory_id = hashlib.md5(f"{text}{category}".encode()).hexdigest()[:16]
        
        try:
            self.collection.upsert(
                ids=[memory_id],
                documents=[text],
                metadatas=[{
                    "category": category,
                    "timestamp": __import__('datetime').datetime.now().isoformat(),
                    **(metadata or {})
                }]
            )
            return True
        except Exception as e:
            print(f"添加记忆失败: {e}")
            return False
    
    def search(self, query: str, category: str = None, n_results: int = 5) -> List[Dict]:
        """语义搜索"""
        if not self.collection:
            return []
        
        try:
            where = {"category": category} if category else None
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            memories = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    memories.append({
                        "text": doc,
                        "distance": results['distances'][0][i] if results['distances'] else 0,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {}
                    })
            return memories
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        if not self.collection:
            return {"status": "disabled", "count": 0}
        return {
            "status": "active",
            "count": self.collection.count(),
            "persist_dir": str(self.persist_dir)
        }

# 全局实例
vector_memory = VectorMemory()
