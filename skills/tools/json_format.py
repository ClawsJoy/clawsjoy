"""JSON 格式化技能"""
import json

class JsonFormatSkill:
    name = "json_format"
    description = "JSON 格式化、压缩、验证"
    version = "1.0.0"
    category = "tools"
    
    def execute(self, params):
        data = params.get("data", "")
        operation = params.get("operation", "format")
        
        try:
            if isinstance(data, str):
                obj = json.loads(data)
            else:
                obj = data
            
            if operation == "format":
                result = json.dumps(obj, indent=2, ensure_ascii=False)
            elif operation == "minify":
                result = json.dumps(obj, separators=(',', ':'), ensure_ascii=False)
            else:
                result = obj
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

skill = JsonFormatSkill()
