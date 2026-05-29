"""火灾报警"""
class FireAlarmSkill:
    def execute(self, params):
        status = params.get('status', 'normal')
        if status == 'alert':
            return {"success": True, "alert": True, "message": "⚠️ 烟雾检测异常！请检查！"}
        return {"success": True, "alert": False, "message": "烟雾传感器正常"}
skill = FireAlarmSkill()
