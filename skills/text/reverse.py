"""
字符串反转
"""
class ReverseSkill:
    name = "reverse"
    description = "字符串反转"
    version = "1.0.0"
    category = "text"
    
    def execute(self, params):
        text = params.get('text', ''); result = text[::-1]
        return {"success": True, "result": result}

skill = ReverseSkill()
