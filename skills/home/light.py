"""灯光控制"""
class LightSkill:
    def execute(self, params):
        room = params.get('room', 'living_room')
        brightness = params.get('brightness', 80)
        color = params.get('color', 'warm')
        return {"success": True, "message": f"{room} 灯光已调至{brightness}% {color}色"}
skill = LightSkill()
