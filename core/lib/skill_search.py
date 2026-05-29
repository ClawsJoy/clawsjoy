from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""技能向量搜索 - 使用专用索引"""

import chromadb
from chromadb.config import Settings

class SkillSearch:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.client = chromadb.PersistentClient(
            path=f"{get_data_root()}/vector_kb",
            settings=Settings(anonymized_telemetry=False)
        )
        try:
            self.collection = self.client.get_collection("skill_vectors")
        except:
            self.collection = None
    
    def search(self, query: str, n: int = 10):
        if not self.collection:
            return []
        results = self.collection.query(query_texts=[query], n_results=n)
        skills = []
        for i, meta in enumerate(results['metadatas'][0]):
            skills.append({
                "name": meta.get('skill_name', 'unknown'),
                "category": meta.get('category', 'general'),
                "description": meta.get('description', ''),
                "score": 1 - results['distances'][0][i] if results['distances'] else 0
            })
        return skills

skill_search = SkillSearch()
