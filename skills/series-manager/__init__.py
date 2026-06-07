\"\"\"series-manager 技能\"\"\"

from .series-manager_skill import series_manager


def execute(params):
    skill = series_manager()
    return skill.execute(params)
