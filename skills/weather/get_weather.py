"""获取天气信息"""
class GetWeatherSkill:
    def execute(self, params):
        city = params.get('city', '上海')
        # TODO: 调用天气 API
        return {
            "success": True,
            "weather": {"city": city, "temp": 22, "condition": "晴"},
            "message": f"{city} 今日天气: 晴, 22°C"
        }
skill = GetWeatherSkill()
