"""
去除空格
"""
class TrimSkill:
    name = "trim"
    description = "去除空格"
    version = "1.0.0"
    category = "text"
    
    def execute(self, params):
        text = params.get('text', ''); result = text.strip()
        return {"success": True, "result": result}

skill = TrimSkill()
