"""文本处理技能"""
import re

class TextProcessorSkill:
    name = "text_processor"
    description = "文本处理：摘要、关键词、统计"
    version = "1.0.0"
    category = "text"
    
    def execute(self, params):
        text = params.get("text", "")
        operation = params.get("operation", "summary")
        
        if not text:
            return {"success": False, "error": "缺少文本"}
        
        if operation == "summary":
            result = text[:100] + "..." if len(text) > 100 else text
        elif operation == "keywords":
            words = re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', text)
            word_freq = {}
            for w in words:
                if len(w) >= 2:
                    word_freq[w] = word_freq.get(w, 0) + 1
            result = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        elif operation == "count":
            result = {
                "chars": len(text),
                "words": len(text.split()),
                "lines": text.count('\n') + 1
            }
        else:
            return {"success": False, "error": f"未知操作: {operation}"}
        
        return {"success": True, "result": result}

skill = TextProcessorSkill()
