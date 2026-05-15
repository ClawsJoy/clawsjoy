"""正则表达式技能"""
import re

class RegexSkill:
    name = "regex"
    description = "正则表达式匹配、替换、提取"
    version = "1.0.0"
    category = "tools"
    
    def execute(self, params):
        text = params.get("text", "")
        pattern = params.get("pattern", "")
        operation = params.get("operation", "match")
        
        try:
            if operation == "match":
                result = re.findall(pattern, text)
            elif operation == "search":
                result = re.search(pattern, text).group() if re.search(pattern, text) else None
            elif operation == "replace":
                replacement = params.get("replacement", "")
                result = re.sub(pattern, replacement, text)
            else:
                result = bool(re.search(pattern, text))
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

skill = RegexSkill()
