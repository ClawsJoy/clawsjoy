\"\"\"video-learn 技能\"\"\"

from .video-learn_skill import video_learn


def execute(params):
    skill = video_learn()
    return skill.execute(params)
