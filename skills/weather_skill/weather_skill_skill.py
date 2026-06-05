"""天气查询技能"""


class WeatherSkill:
    name = "weather_skill"
    description = "查询天气"
    version = "1.0.0"
    category = "utility"

    def execute(self, params):
        city = params.get("city", "北京")
        # 模拟天气数据
        weathers = ["晴 ☀️", "多云 ⛅", "阴 ☁️", "小雨 🌧️", "雪 ❄️"]
        import random

        weather = random.choice(weathers)
        return {
            "success": True,
            "result": f"{city}天气：{weather}",
            "city": city,
            "weather": weather,
        }


skill = WeatherSkill()
