\"\"\"workflow-engine 技能\"\"\"

from .workflow-engine_skill import workflow_engine


def execute(params):
    skill = workflow_engine()
    return skill.execute(params)
