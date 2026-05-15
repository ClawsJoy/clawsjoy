from skills.skill_interface import BaseSkill

class WeatherSkill(BaseSkill):
    name = "weather"
    description = "查询天气"
    version = "1.0.0"
    category = "utility"
    
    def execute(self, params):
        city = params.get("city", "北京")
        return {"success": True, "weather": f"{city} 晴天 25°C"}

skill = WeatherSkill()
