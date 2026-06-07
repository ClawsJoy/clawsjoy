""""""

import subprocess
from pathlib import Path


class VideoFeedbackSkill:
    name = "video-feedback"
    description = "根据反馈调整视频"
    version = "1.0.0"

    def execute(self, params):
        video_path = params.get("video_path", "")
        feedback = params.get("feedback", "")

        if not video_path:
            return {"success": False, "error": "请提供视频路径"}

        path = Path(video_path)
        if not path.exists():
            return {"success": False, "error": f"文件不存在: {video_path}"}

        brightness = 0.15 if "太暗" in feedback else (-0.1 if "太亮" in feedback else 0)
        output_path = path.parent / f"{path.stem}_adjusted.mp4"

        if brightness != 0:
            cmd = [
                "ffmpeg",
                "-i",
                str(path),
                "-vf",
                f"eq=brightness={1+brightness}",
                "-c:a",
                "copy",
                "-y",
                str(output_path),
            ]
            subprocess.run(cmd, capture_output=True)
            return {"success": True, "result": "视频已调整", "output": str(output_path)}

        return {"success": True, "result": "无需调整"}
