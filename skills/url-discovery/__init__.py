\"\"\"url-discovery 技能\"\"\"

from .url-discovery_skill import url_discovery


def execute(params):
    skill = url_discovery()
    return skill.execute(params)
