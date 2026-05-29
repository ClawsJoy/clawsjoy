"""乘法技能"""
class MultiplySkill:
    def execute(self, params):
        return {"success": True, "result": params.get('a', 0) * params.get('b', 0)}
skill = MultiplySkill()
