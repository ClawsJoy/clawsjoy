""""""

import base64
import subprocess
from pathlib import Path

import requests


class VideoSceneSkill:
    name = "video-scene"
    description = "识别视频场景"
    version = "1.0.0"

    def execute(self, params):
        video_path = params.get("video_path", "")
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
                    "prompt": "场景类型",
                    "images": [image_base64],
                    "stream": False,
                },
                timeout=30,
            )
            scene = (
                r.json().get("response", "unknown")
                if r.status_code == 200
                else "unknown"
            )
            return {"success": True, "result": scene, "scene_type": scene}
        except Exception as e:
            return {"success": True, "result": "unknown", "scene_type": "unknown"}
