"""JSON格式化"""
import json
class FormatJsonSkill:
    def execute(self, params):
        data = params.get('data', {})
        try:
            if isinstance(data, str):
                data = json.loads(data)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            return {"success": True, "result": formatted}
        except:
            return {"success": False, "error": "无效JSON"}
skill = FormatJsonSkill()
