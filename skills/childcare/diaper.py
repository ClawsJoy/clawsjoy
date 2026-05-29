"""尿布记录"""
class DiaperSkill:
    def execute(self, params):
        time = params.get('time', '')
        status = params.get('status', 'wet')  # wet/dry/dirty
        return {"success": True, "message": f"{time} 更换尿布，状态: {status}"}
skill = DiaperSkill()
