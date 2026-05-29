from lib.smart_config import smart_config
"""multiply技能"""
class MultiplySkill:
    name = "multiply"
    description = "multiply运算"
    version = "1.0.0"
    category = "math"
    
    def execute(self, params):
        a = params.get("a", 0)
        b = params.get("b", 0)
        if "multiply" == "multiply":
            result = a * b
        elif "multiply" == "divide":
            result = a / b if b != 0 else 0
        else:
            result = a - b
        return {"success": True, "result": result}

skill = MultiplySkill()
