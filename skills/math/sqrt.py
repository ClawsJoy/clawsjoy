"""
平方根
"""
class SqrtSkill:
    name = "sqrt"
    description = "平方根"
    version = "1.0.0"
    category = "math"
    
    def execute(self, params):
        import math; a = params.get('a', 0); result = math.sqrt(a)
        return {"success": True, "result": result}

skill = SqrtSkill()
