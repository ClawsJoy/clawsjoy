"""窗帘控制"""
class CurtainSkill:
    def execute(self, params):
        action = params.get('action', 'open')  # open/close
        percentage = params.get('percentage', 100)
        return {"success": True, "message": f"窗帘已{action} {percentage}%"}
skill = CurtainSkill()
