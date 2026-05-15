"""加法技能"""
class AddSkill:
    name = "add"
    description = "两数相加"
    version = "1.0.0"
    category = "math"
    
    def execute(self, params):
        a = params.get("a", 0)
        b = params.get("b", 0)
        result = a + b
        return {"success": True, "result": result, "expression": f"{a} + {b} = {result}"}

skill = AddSkill()
