\"\"\"expert-script-writer 技能\"\"\"

from .expert-script-writer_skill import expert_script_writer


def execute(params):
    skill = expert_script_writer()
    return skill.execute(params)
