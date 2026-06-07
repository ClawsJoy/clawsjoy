\"\"\"weather 技能\"\"\"

from .weather_skill import weather


def execute(params):
    skill = weather()
    return skill.execute(params)
