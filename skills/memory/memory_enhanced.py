"""增强版记忆技能 - 支持向量检索和语义搜索"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from lib.memory_simple import memory
from lib.memory_vector import vector_memory

class MemoryEnhancedSkill:
    name = "memory_enhanced"
    description = "增强版记忆，支持关键词搜索和语义检索"
    version = "2.0.0"
    category = "memory"
    
    def execute(self, params):
        operation = params.get("operation", "recall")
        
        if operation == "recall":
            category = params.get("category")
            if category:
                items = memory.recall_all(category=category)
                return {"success": True, "result": items[-20:], "count": len(items)}
            return {"success": False, "error": "需要 category 参数"}
        
        elif operation == "remember":
            fact = params.get("fact")
            category = params.get("category", "general")
            if fact:
                memory.remember(fact, category=category)
                return {"success": True, "message": f"已记忆: {fact[:50]}..."}
            return {"success": False, "error": "需要 fact 参数"}
        
        elif operation == "search":
            query = params.get("query")
            category = params.get("category")
            if query:
                results = vector_memory.search(query, category, n_results=5)
                return {"success": True, "results": results}
            return {"success": False, "error": "需要 query 参数"}
        
        elif operation == "stats":
            categories = memory.memories.get('categories', {})
            stats = {cat: len(items) for cat, items in categories.items()}
            stats['vector_status'] = vector_memory.get_stats()
            return {"success": True, "stats": stats}
        
        return {"success": False, "error": f"未知操作: {operation}"}

skill = MemoryEnhancedSkill()
