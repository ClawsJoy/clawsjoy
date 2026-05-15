"""
转小写
"""
class To_lowerSkill:
    name = "to_lower"
    description = "转小写"
    version = "1.0.0"
    category = "text"
    
    def execute(self, params):
        text = params.get('text', ''); result = text.lower()
        return {"success": True, "result": result}

skill = To_lowerSkill()
