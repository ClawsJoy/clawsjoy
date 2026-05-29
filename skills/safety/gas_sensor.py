"""燃气报警"""
class GasSensorSkill:
    def execute(self, params):
        level = params.get('level', 0)
        if level > 50:
            return {"success": True, "alert": True, "message": "⚠️ 燃气浓度过高！请开窗通风！"}
        return {"success": True, "alert": False, "message": f"燃气浓度 {level}"}
skill = GasSensorSkill()
