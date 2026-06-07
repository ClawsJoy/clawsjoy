#!/usr/bin/env python3
"""视频场景识别 - 识别视频中的场景类型"""

import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/flybo/clawsjoy_v5")
from tools.video.frame_extractor import extract_frames


class VideoSceneSkill:
    name = "video-scene"
    description = "识别视频场景类型"
    version = "1.0.0"

    def execute(self, params):
        video_path = params.get("video_path", "")

        if not video_path:
            return {"success": False, "error": "请提供视频路径"}

        path = Path(video_path)
        if not path.exists():
            return {"success": False, "error": f"文件不存在: {video_path}"}

        frames = extract_frames(str(path), num_frames=5)
        if frames.get("error"):
            return {"success": False, "error": frames["error"]}

        scenes = []
        for frame_path in frames.get("frames", []):
            scene = self._recognize_scene(frame_path)
            scenes.append(scene)

        # 综合判断
        final_scene = self._determine_scene(scenes)

        return {
            "success": True,
            "video": video_path,
            "scene_type": final_scene,
            "confidence": 0.8,
            "details": scenes,
        }

    def _recognize_scene(self, frame_path):
        """识别单帧场景"""
        try:
            import base64

            import requests

            with open(frame_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode()

            prompt = """分析这个画面，只回答场景类型（选一个）：
- tutorial: 教学/教程画面（有代码、文档、讲解）
- presentation: 演示/PPT画面
- talking_head: 人像讲话（有人在说话）
- screen_capture: 屏幕录制
- other: 其他"""

            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "moondream:1.8b",
                    "prompt": prompt,
                    "images": [image_base64],
                    "stream": False,
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "other").strip().lower()
        except:
            pass
        return "other"

    def _determine_scene(self, scenes):
        """综合判断场景类型"""
        from collections import Counter

        counter = Counter(scenes)
        if counter:
            return counter.most_common(1)[0][0]
        return "other"


if __name__ == "__main__":
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    skill = VideoSceneSkill()
    result = skill.execute(params)
    print(json.dumps(result, ensure_ascii=False))


def execute(params):
    skill = VideoSceneSkill()
    return skill.execute(params)
