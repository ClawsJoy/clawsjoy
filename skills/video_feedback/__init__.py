"""video_feedback 技能"""

from .video_feedback_skill import VideoFeedbackSkill


def execute(params=None):
    if params is None:
        params = {}
    return VideoFeedbackSkill().execute(params)
