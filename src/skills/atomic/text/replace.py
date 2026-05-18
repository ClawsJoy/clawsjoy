from lib.smart_config import smart_config
"""查找替换"""
class ReplaceSkill:
    name = "replace"
    description = "文本查找替换"
    version = "1.0.0"
    category = "text"
    
    def execute(self, params):
        text = params.get("text", "")
        old = params.get("old", "")
        new = params.get("new", "")
        
        if not text or not old:
            return {"success": False, "error": "需要提供文本和查找内容"}
        
        result = text.replace(old, new)
        count = text.count(old)
        
        return {"success": True, "result": result, "replaced_count": count}

skill = ReplaceSkill()
