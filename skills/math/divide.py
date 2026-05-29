"""除法技能"""
class DivideSkill:
    def execute(self, params):
        b = params.get('b', 1)
        if b == 0:
            return {"success": False, "error": "除数不能为0"}
        return {"success": True, "result": params.get('a', 0) / b}
skill = DivideSkill()
