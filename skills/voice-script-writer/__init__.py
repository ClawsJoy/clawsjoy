\"\"\"voice-script-writer 技能\"\"\"

from .voice-script-writer_skill import voice_script_writer


def execute(params):
    skill = voice_script_writer()
    return skill.execute(params)
