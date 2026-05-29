from lib.smart_config import smart_config
"""字数统计"""
class WordCountSkill:
    name = "word_count"
    description = "统计文本字数"
    version = "1.0.0"
    category = "text"
    
    def execute(self, params):
        text = params.get("text", "")
        words = len(text.split())
        chars = len(text)
        return {"success": True, "words": words, "chars": chars, "text": text[:50]}

skill = WordCountSkill()
