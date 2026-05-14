"""除法技能"""
class DivideSkill:
    name = "divide"
    description = "两数相除"
    version = "1.0.0"
    category = "math"
    
    def execute(self, params):
        a = params.get("a", 0)
        b = params.get("b", 1)
        if b == 0:
            return {"success": False, "error": "除数不能为0"}
        result = a / b
        return {"success": True, "result": result, "expression": f"{a} ÷ {b} = {result}"}

skill = DivideSkill()
