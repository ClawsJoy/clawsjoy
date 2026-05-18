from lib.smart_config import smart_config
"""字数统计"""
class CountWordsSkill:
    name = "count_words"
    description = "统计文本字数"
    version = "1.0.0"
    category = "text"
    
    def execute(self, params):
        text = params.get("text", "")
        if not text:
            return {"success": False, "error": "需要提供文本"}
        
        chars = len(text)
        words = len(text.split())
        lines = text.count('\n') + 1
        
        return {
            "success": True,
            "chars": chars,
            "words": words,
            "lines": lines,
            "text_length": chars
        }

skill = CountWordsSkill()
