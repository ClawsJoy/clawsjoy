\"\"\"pro-script-writer 技能\"\"\"

from .pro-script-writer_skill import pro_script_writer


def execute(params):
    skill = pro_script_writer()
    return skill.execute(params)
