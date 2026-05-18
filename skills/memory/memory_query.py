"""记忆查询技能"""
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from lib.memory_vector import VectorMemory

class MemoryQuerySkill:
    name = "memory_query"
    description = "查询向量记忆"
    version = "1.0.0"
    category = "memory"

    def execute(self, params):
        query = params.get("query", "")
        n = params.get("n", 10)

        if not query:
            return {"success": False, "error": "需要 query 参数"}

        vm = VectorMemory()
        results = vm.search(query, n=n)

        formatted = []
        for r in results:
            formatted.append({
                "text": r['text'][:300],
                "category": r['metadata'].get('category'),
                "similarity": r['similarity']
            })

        return {
            "success": True,
            "query": query,
            "count": len(formatted),
            "results": formatted
        }

skill = MemoryQuerySkill()
