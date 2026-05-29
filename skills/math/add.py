"""加法技能"""
class AddSkill:
    def execute(self, params):
        a = params.get('a', 0)
        b = params.get('b', 0)
        return {"success": True, "result": a + b}
skill = AddSkill()
