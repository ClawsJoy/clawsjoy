"""
幂运算
"""
class PowerSkill:
    name = "power"
    description = "幂运算"
    version = "1.0.0"
    category = "math"
    
    def execute(self, params):
        a = params.get('a', 0); b = params.get('b', 1); result = a ** b
        return {"success": True, "result": result}

skill = PowerSkill()
