\"\"\"workflow-engine-v2 技能\"\"\"

from .workflow-engine-v2_skill import workflow_engine_v2


def execute(params):
    skill = workflow_engine_v2()
    return skill.execute(params)
