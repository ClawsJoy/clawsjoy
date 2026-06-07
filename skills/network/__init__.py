\"\"\"network 技能\"\"\"

from .network_skill import network


def execute(params):
    skill = network()
    return skill.execute(params)
