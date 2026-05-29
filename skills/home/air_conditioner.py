"""空调控制"""
class AirConditionerSkill:
    def execute(self, params):
        action = params.get('action', 'on')  # on/off
        temp = params.get('temp', 26)
        mode = params.get('mode', 'cool')  # cool/heat/fan
        return {"success": True, "message": f"空调已{action}，温度{temp}°C，模式{mode}"}
skill = AirConditionerSkill()
