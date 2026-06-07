#!/usr/bin/env python3
"""视频理解 - 使用本地视觉模型分析视频内容"""

import base64
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/home/flybo/clawsjoy_v5")
from tools.video.frame_extractor import extract_frames


class VideoUnderstandSkill:
    name = "video-understand"
    description = "使用视觉模型理解视频内容"
    version = "1.0.0"

    MODELS = {"fast": "moondream:1.8b", "accurate": "llava:7b"}

    def execute(self, params):
        video_path = params.get("video_path", "")
        model_type = params.get("model", "fast")
        questions = params.get("questions", ["描述这个画面"])

        if not video_path:
            return {"success": False, "error": "请提供视频路径"}

        path = Path(video_path)
        if not path.exists():
            return {"success": False, "error": f"文件不存在: {video_path}"}

        # 提取关键帧
        frames = extract_frames(str(path), num_frames=3)
        if frames.get("error"):
            return {"success": False, "error": frames["error"]}

        model = self.MODELS.get(model_type, self.MODELS["fast"])
        analyses = []

        for frame_path in frames.get("frames", []):
            frame_analysis = {}
            for question in questions:
                try:
                    # 使用 ollama API 格式
                    import requests

                    # 读取图片并转为 base64
                    with open(frame_path, "rb") as f:
                        image_base64 = base64.b64encode(f.read()).decode()

                    # 调用 ollama API
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
                        frame_analysis[question] = result.get("response", "无响应")
                    else:
                        frame_analysis[question] = f"API错误: {response.status_code}"
                except Exception as e:
                    frame_analysis[question] = f"分析失败: {str(e)}"

            analyses.append({"frame": frame_path, "analysis": frame_analysis})

        summary = self._generate_summary(analyses)

        return {
            "success": True,
            "video": video_path,
            "duration": frames.get("duration", 0),
            "model_used": model,
            "frames_analyzed": len(frames.get("frames", [])),
            "detailed_analysis": analyses,
            "summary": summary,
        }

    def _generate_summary(self, analyses):
        if not analyses:
            return "无法分析"
        summaries = []
        for i, frame in enumerate(analyses):
            for q, a in frame.get("analysis", {}).items():
                if a and "失败" not in a and "错误" not in a:
                    summaries.append(f"帧{i+1}: {a[:100]}")
        return "; ".join(summaries) if summaries else "分析完成"


if __name__ == "__main__":
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    skill = VideoUnderstandSkill()
    result = skill.execute(params)
    print(json.dumps(result, ensure_ascii=False))
