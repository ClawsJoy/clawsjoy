from lib.smart_config import smart_config
"""SHA256哈希"""
import hashlib

class Sha256Skill:
    name = "sha256"
    description = "计算文本的 SHA256 哈希值"
    version = "1.0.0"
    category = "hash"
    
    def execute(self, params):
        text = params.get("text", "")
        if not text:
            return {"success": False, "error": "需要提供文本"}
        
        result = hashlib.sha256(text.encode()).hexdigest()
        return {"success": True, "sha256": result, "text": text}

skill = Sha256Skill()
