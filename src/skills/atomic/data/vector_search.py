"""向量检索技能"""
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from src.lib.vector.vector_manager import vector_manager

class VectorSearchSkill:
    name = "vector_search"
    description = "向量检索知识库"
    version = "1.0.0"
    category = "data"
    
    def execute(self, params):
        query = params.get("query", "")
        top_k = params.get("top_k", 5)
        
        if not query:
            return {"success": False, "error": "需要提供查询"}
        
        results = vector_manager.search(query, top_k)
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }

skill = VectorSearchSkill()
