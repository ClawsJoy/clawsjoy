from lib.smart_config import smart_config
"""divide技能"""
class DivideSkill:
    name = "divide"
    description = "divide运算"
    version = "1.0.0"
    category = "math"
    
    def execute(self, params):
        a = params.get("a", 0)
        b = params.get("b", 0)
        if "divide" == "multiply":
            result = a * b
        elif "divide" == "divide":
            result = a / b if b != 0 else 0
        else:
            result = a - b
        return {"success": True, "result": result}

skill = DivideSkill()
