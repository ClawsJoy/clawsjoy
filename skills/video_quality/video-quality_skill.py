""""""

import json
import subprocess
from pathlib import Path


class VideoQualitySkill:
    name = "video-quality"
    description = "分析视频画质"
    version = "1.0.0"

    def execute(self, params):
        video_path = params.get("video_path", "")
        if not video_path:
            return {"success": False, "error": "请提供视频路径"}

        path = Path(video_path)
        if not path.exists():
            return {"success": False, "error": f"文件不存在: {video_path}"}

        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_streams",
            str(path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)

        for s in data.get("streams", []):
            if s.get("codec_type") == "video":
                w, h = s.get("width", 0), s.get("height", 0)
                quality = (
                    "4K"
                    if w >= 3840
                    else "1080p" if w >= 1920 else "720p" if w >= 1280 else "SD"
                )
                return {
                    "success": True,
                    "result": f"{w}x{h}, {quality}",
                    "resolution": f"{w}x{h}",
                    "quality": quality,
                }

        return {"success": False, "error": "未找到视频流"}
