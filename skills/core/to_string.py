"""转换为字符串技能"""

class ToStringSkill:
    name = "to_string"
    description = "将任意值转换为字符串"
    version = "1.0.0"
    category = "core"
    
    def execute(self, params: dict) -> dict:
        value = params.get('value', '')
        return {"success": True, "result": str(value)}

skill = ToStringSkill()
