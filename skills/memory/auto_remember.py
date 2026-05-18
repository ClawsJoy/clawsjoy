"""自动记忆 - 重要信息自动入库"""
import sys
from datetime import datetime
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from lib.memory_vector import VectorMemory

class AutoRememberSkill:
    name = "auto_remember"
    description = "自动记录重要信息到向量记忆"
    version = "1.0.0"
    category = "memory"
    
    def execute(self, params):
        content = params.get("content", "")
        category = params.get("category", "auto_log")
        source = params.get("source", "user")
        
        if not content:
            return {"success": False, "error": "需要 content 参数"}
        
        vector_memory = VectorMemory()
        
        # 添加时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_text = f"[{timestamp}][{source}] {content}"
        
        doc_id = vector_memory.add(
            text=full_text,
            category=category,
            metadata={"source": source, "timestamp": timestamp}
        )
        
        return {
            "success": True,
            "doc_id": doc_id,
            "category": category,
            "timestamp": timestamp,
            "content": content[:100]
        }

skill = AutoRememberSkill()
