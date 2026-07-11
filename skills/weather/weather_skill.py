#!/usr/bin/env python3
"""Weather Skill - 天气查询技能（演示模式，不造假）"""

import random
from datetime import datetime


class WeatherSkill:
    """天气查询技能 - 只展示意图识别和路由，不返回假数据"""

    name = "weather_skill"
    description = "天气查询（演示模式）"

    def execute(self, params: dict) -> dict:
        city = params.get("city", "")
        
        if not city:
            return {
                "success": False,
                "message": "📍 请指定城市名称，例如：北京天气"
            }
        
        # ✅ 真实展示：识别到城市，但返回真实状态（不伪造数据）
        return {
            "success": True,
            "message": f"""
🌤️ 天气查询请求已识别

📍 城市：{city}
📌 状态：已路由到天气技能
🔧 说明：当前为演示模式，展示意图识别和 Agent 路由功能

💡 下一步：接入真实天气 API 后可返回实时数据
""",
            "data": {
                "city": city,
                "status": "recognized",
                "mode": "demo"
            }
        }


weather_skill = WeatherSkill()
