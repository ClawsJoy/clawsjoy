#!/usr/bin/env python3
"""示例自定义技能 - 符合 OpenClaw 规范"""

import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.skill_system_v2 import BaseSkill, SkillManifest, SkillCategory, SkillPermission

class WeatherSkill(BaseSkill):
    """天气查询技能"""
    
    def _get_manifest(self):
        return SkillManifest(
            name="weather_query",
            version="1.0.0",
            description="Get weather information for a city",
            author="ClawsJoy",
            category=SkillCategory.NETWORK,
            permissions=SkillPermission.PUBLIC,
            inputs=[
                {"name": "city", "type": "string", "required": True, "description": "City name"},
                {"name": "units", "type": "string", "default": "metric", "description": "Units: metric/imperial"}
            ],
            outputs=[
                {"name": "temperature", "type": "number", "description": "Temperature"},
                {"name": "condition", "type": "string", "description": "Weather condition"},
                {"name": "humidity", "type": "number", "description": "Humidity percentage"}
            ],
            examples=["weather_query city='Beijing'", "weather_query city='London' units='metric'"]
        )
    
    def execute(self, params):
        city = params.get('city', '')
        if not city:
            return {'success': False, 'error': 'City name required'}
        
        # 模拟天气数据（实际可接入真实 API）
        return {
            'success': True,
            'city': city,
            'temperature': 22,
            'condition': 'Sunny',
            'humidity': 65,
            'message': f"Weather in {city}: 22°C, Sunny"
        }

# 自动注册
if __name__ != '__main__':
    weather_skill = WeatherSkill()
