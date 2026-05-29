"""ClawsJoy 长期记忆库 - 配置驱动"""

import chromadb
from pathlib import Path
import hashlib
from core.lib.unified_config import unified_config


class ClawsJoyMemory:
    def __init__(self, persist_dir=None):
        vector_config = unified_config.get("vector", {})
        if persist_dir is None:
            data_root = unified_config.get("paths.data_root", "data")
            persist_dir = vector_config.get("db_path", f"{data_root}/chroma/memory")
        
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        
        embedding_model = vector_config.get("embedding_model", "nomic-embed-text")
        from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
        ollama_url = unified_config.get("llm.endpoint", "http://localhost:11434")
        self.embedding_fn = OllamaEmbeddingFunction(url=ollama_url, model_name=embedding_model)
        
        self.client = chromadb.PersistentClient(path=persist_dir)
        collection_name = vector_config.get("collection_name", "clawsjoy_memory")
        
        try:
            self.collection = self.client.get_collection(collection_name)
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )

    def remember(self, fact, category="general", user_id="default"):
        doc_id = hashlib.md5(f"{user_id}:{fact}".encode()).hexdigest()
        self.collection.upsert(
            ids=[doc_id],
            documents=[fact],
            metadatas=[{"category": category, "user_id": user_id}]
        )
        return True

    def recall(self, query, category=None, user_id=None, n=5, min_similarity=None):
        if min_similarity is None:
            try:
                from core.lib.unified_config import unified_config
                vector_config = unified_config.get("vector", {})
                retrieval_config = vector_config.get("retrieval", {})
                min_similarity = retrieval_config.get("similarity_threshold", 0.5)
            except:
                min_similarity = 0.5
        
        # 构建 where 条件（使用 $and 语法）
        where_conditions = []
        if user_id:
            where_conditions.append({"user_id": user_id})
        if category:
            where_conditions.append({"category": category})
        
        if len(where_conditions) == 1:
            query_where = where_conditions[0]
        elif len(where_conditions) > 1:
            query_where = {"$and": where_conditions}
        else:
            query_where = None
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n * 3,
                where=query_where,
                include=["documents", "distances"]
            )
        except Exception as e:
            print(f"召回错误: {e}")
            return []
        
        if not results.get("documents") or not results["documents"][0]:
            return []
        
        items = []
        for i, doc in enumerate(results["documents"][0]):
            distance = results["distances"][0][i] if results.get("distances") else 1.0
            similarity = 1.0 / (1.0 + distance)
            if similarity >= min_similarity:
                items.append((similarity, doc))
        
        items.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in items[:n]]
    def get_stats(self):
        return {"total_memories": self.collection.count()}


memory = ClawsJoyMemory()
