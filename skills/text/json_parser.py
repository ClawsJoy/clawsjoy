"""JSON 解析技能"""
import json

class JSONParserSkill:
    name = "json_parser"
    description = "解析和处理 JSON 数据"
    version = "1.0.0"
    category = "data"
    
    def execute(self, params):
        data = params.get("data", "")
        operation = params.get("operation", "parse")
        
        try:
            if operation == "parse":
                if isinstance(data, str):
                    result = json.loads(data)
                else:
                    result = data
                return {"success": True, "result": result}
            elif operation == "stringify":
                result = json.dumps(data, ensure_ascii=False, indent=2)
                return {"success": True, "result": result}
            else:
                return {"success": False, "error": f"未知操作: {operation}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

skill = JSONParserSkill()
