\"\"\"dual-script-writer 技能\"\"\"

from .dual-script-writer_skill import dual_script_writer


def execute(params):
    skill = dual_script_writer()
    return skill.execute(params)
