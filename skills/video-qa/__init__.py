\"\"\"video-qa 技能\"\"\"

from .video-qa_skill import video_qa


def execute(params):
    skill = video_qa()
    return skill.execute(params)
