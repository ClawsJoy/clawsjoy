#!/usr/bin/env python3
"""视频裁剪技能"""

import json
import subprocess
import sys
from pathlib import Path


class VideoTrimSkill:
    name = "video-trim"
    description = "视频裁剪"
    version = "1.0.0"

    def execute(self, params):
        video_path = params.get("video_path", "")
        start = params.get("start", 0)
        end = params.get("end", 0)
        duration = params.get("duration", 0)

        if not video_path:
            return {"success": False, "error": "请提供视频路径"}

        path = Path(video_path)
        if not path.exists():
            return {"success": False, "error": f"文件不存在: {video_path}"}

        # 统一转为数字
        if isinstance(start, str):
            start = self._parse_time(start)
        if isinstance(end, str):
            end = self._parse_time(end)
        if isinstance(duration, str):
            duration = self._parse_time(duration)

        if duration:
            output_path = path.parent / f"{path.stem}_trimmed_{start}_{duration}.mp4"
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(path),
                "-ss",
                str(start),
                "-t",
                str(duration),
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-pix_fmt",
                "yuv420p",
                "-an",
                str(output_path),
            ]
        elif end:
            duration = end - start
            output_path = path.parent / f"{path.stem}_trimmed_{start}_{end}.mp4"
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(path),
                "-ss",
                str(start),
                "-t",
                str(duration),
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-pix_fmt",
                "yuv420p",
                "-an",
                str(output_path),
            ]
        else:
            return {"success": False, "error": "请指定开始和结束时间"}

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and output_path.exists():
                return {
                    "success": True,
                    "result": f"裁剪完成: {output_path.name}",
                    "output_path": str(output_path),
                }
            return {
                "success": False,
                "error": result.stderr[:200] if result.stderr else "未知错误",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_time(self, time_str):
        if isinstance(time_str, (int, float)):
            return time_str
        if ":" in time_str:
            parts = time_str.split(":")
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
        return int(time_str) if str(time_str).isdigit() else 0


def execute(params):
    skill = VideoTrimSkill()
    return skill.execute(params)


if __name__ == "__main__":
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = execute(params)
    print(json.dumps(result, ensure_ascii=False))
