"""天气查询"""
class weather_skill:
    name = "weather"
    description = "天气查询"
    version = "1.0.0"
    def execute(self, params):
        city = params.get("city", "北京")
        return {"success": True, "city": city, "weather": "晴", "temp": "25°C", "tip": "如需实时天气请联网"}
