"""
转大写
"""
class To_upperSkill:
    name = "to_upper"
    description = "转大写"
    version = "1.0.0"
    category = "text"
    
    def execute(self, params):
        text = params.get('text', ''); result = text.upper()
        return {"success": True, "result": result}

skill = To_upperSkill()
