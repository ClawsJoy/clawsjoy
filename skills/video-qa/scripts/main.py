#!/usr/bin/env python3
"""视频问答 - 针对视频内容提问"""

import base64
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/home/flybo/clawsjoy_v5")
from tools.video.frame_extractor import extract_frames


class VideoQASkill:
    name = "video-qa"
    description = "视频内容问答"
    version = "1.0.0"

    MODELS = {"fast": "moondream:1.8b", "accurate": "llava:7b"}

    def execute(self, params):
        video_path = params.get("video_path", "")
        question = params.get("question", "描述这个视频")
        model_type = params.get("model", "fast")

        if not video_path:
            return {"success": False, "error": "请提供视频路径"}

        path = Path(video_path)
        if not path.exists():
            return {"success": False, "error": f"文件不存在: {video_path}"}

        # 提取关键帧
        frames = extract_frames(str(path), num_frames=5)
        if frames.get("error"):
            return {"success": False, "error": frames["error"]}

        model = self.MODELS.get(model_type, self.MODELS["fast"])

        # 对多个帧进行问答，综合答案
        answers = []
        for frame_path in frames.get("frames", []):
            try:
                import requests

                with open(frame_path, "rb") as f:
                    image_base64 = base64.b64encode(f.read()).decode()

                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model,
                        "prompt": question,
                        "images": [image_base64],
                        "stream": False,
                    },
                    timeout=60,
                )

                if response.status_code == 200:
                    result = response.json()
                    answers.append(result.get("response", ""))
            except Exception as e:
                continue

        # 综合多帧答案
        final_answer = self._aggregate_answers(answers, question)

        return {
            "success": True,
            "video": video_path,
            "question": question,
            "answer": final_answer,
            "frames_analyzed": len(answers),
            "model_used": model,
        }

    def _aggregate_answers(self, answers, question):
        """综合多帧答案"""
        if not answers:
            return "无法分析视频内容"

        # 简单综合：取第一个非空答案
        for ans in answers:
            if ans and len(ans) > 10:
                return ans.strip()
        return answers[0] if answers else "无法回答"


if __name__ == "__main__":
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    skill = VideoQASkill()
    result = skill.execute(params)
    print(json.dumps(result, ensure_ascii=False))


def execute(params):
    skill = VideoQASkill()
    return skill.execute(params)
