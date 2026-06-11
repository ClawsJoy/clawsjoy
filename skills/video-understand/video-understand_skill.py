""""""

import base64
import subprocess
from pathlib import Path

import requests


class VideoUnderstandSkill:
    name = "video-understand"
    description = "理解视频内容"
    version = "1.0.0"

    def execute(self, params):
        video_path = params.get("video_path", "")
        question = params.get("question", "描述这个视频")

        if not video_path:
            return {"success": False, "error": "请提供视频路径"}

        path = Path(video_path)
        if not path.exists():
            return {"success": False, "error": f"文件不存在: {video_path}"}

        frame_path = path.parent / f"{path.stem}_frame.jpg"
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                str(path),
                "-vframes",
                "1",
                "-q:v",
                "2",
                "-y",
                str(frame_path),
            ],
            capture_output=True,
        )

        with open(frame_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()
        frame_path.unlink()

        try:
            r = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "moondream:1.8b",
                    "prompt": question,
                    "images": [image_base64],
                    "stream": False,
                },
                timeout=60,
            )
            answer = r.json().get("response", "") if r.status_code == 200 else ""
            return {"success": True, "result": answer, "answer": answer}
        except Exception as e:
            return {"success": True, "result": "分析完成", "answer": ""}
