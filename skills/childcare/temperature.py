"""体温监测"""
class TemperatureSkill:
    def execute(self, params):
        temp = params.get('temp', 36.5)
        location = params.get('location', '腋下')
        return {"success": True, "message": f"体温: {temp}°C ({location})", "alert": temp > 37.5}
skill = TemperatureSkill()
