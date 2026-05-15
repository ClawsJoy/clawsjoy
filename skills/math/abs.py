"""
绝对值
"""
class AbsSkill:
    name = "abs"
    description = "绝对值"
    version = "1.0.0"
    category = "math"
    
    def execute(self, params):
        a = params.get('a', 0); result = abs(a)
        return {"success": True, "result": result}

skill = AbsSkill()
