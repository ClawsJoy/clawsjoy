"""
weather_skill 技能模块
"""

from .weather_skill_skill import WeatherSkill


def execute(params=None):
    """统一执行入口"""
    skill = WeatherSkill()
    return skill.execute(params)
