"""门锁控制"""
class DoorLockSkill:
    def execute(self, params):
        action = params.get('action', 'lock')
        return {"success": True, "message": f"门已{action}", "status": action}
skill = DoorLockSkill()
