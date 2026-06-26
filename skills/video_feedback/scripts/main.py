#!/usr/bin/env python3
"""视频反馈技能 - 自然语言调整视频"""

import json
import re
import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")
from engine.chain.video_feedback_chain import VideoFeedbackAgent


def execute(params):
    video_path = params.get("video_path", "")
    feedback = params.get("feedback", "")

    if not video_path or not feedback:
        return {"success": False, "error": "需要 video_path 和 feedback"}

    agent = VideoFeedbackAgent()
    result = agent.handle(f"{video_path} {feedback}")

    return {
        "success": result.get("success", False),
        "response": result.get("response", ""),
        "adjusted_video": result.get("adjusted_video"),
    }


if __name__ == "__main__":
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = execute(params)
    print(json.dumps(result, ensure_ascii=False))
