\"\"\"file-service-skill 技能\"\"\"

from .file-service-skill_skill import file_service_skill


def execute(params):
    skill = file_service_skill()
    return skill.execute(params)
