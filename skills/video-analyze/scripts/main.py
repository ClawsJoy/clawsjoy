#!/usr/bin/env python3
"""视频分析技能 - 增强版"""

import json
import subprocess
import sys
from pathlib import Path


class VideoAnalyze:
    name = "video-analyze"
    description = "分析本地视频文件"
    version = "1.1.0"

    def execute(self, params):
        video_path = params.get("video_path", "")
        if not video_path:
            return {"success": False, "error": "请提供视频文件路径"}

        path = Path(video_path)
        if not path.exists():
            return {"success": False, "error": f"文件不存在: {video_path}"}

        # 获取文件大小
        size_mb = round(path.stat().st_size / 1024 / 1024, 2)

        # 使用 ffprobe 获取视频信息
        try:
            cmd = [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                str(path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)

            video_stream = None
            audio_stream = None
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    video_stream = stream
                elif stream.get("codec_type") == "audio":
                    audio_stream = stream

            duration = float(data.get("format", {}).get("duration", 0))
            bit_rate = data.get("format", {}).get("bit_rate", "N/A")

            # 计算码率（如果未提供）
            if bit_rate == "N/A" and duration > 0:
                bit_rate = int(path.stat().st_size * 8 / duration)

            # 帧率
            frame_rate = (
                video_stream.get("r_frame_rate", "N/A") if video_stream else "N/A"
            )
            # 简化帧率显示（如 "30000/1001" -> "29.97"）
            if "/" in str(frame_rate):
                try:
                    num, den = frame_rate.split("/")
                    frame_rate = round(float(num) / float(den), 2)
                except:
                    pass

            return {
                "success": True,
                "file_name": path.name,
                "size_mb": size_mb,
                "duration_seconds": duration,
                "duration_formatted": f"{int(duration//60)}:{int(duration%60):02d}",
                "resolution": (
                    f"{video_stream.get('width', 'N/A')}x{video_stream.get('height', 'N/A')}"
                    if video_stream
                    else "N/A"
                ),
                "codec": (
                    video_stream.get("codec_name", "N/A") if video_stream else "N/A"
                ),
                "frame_rate": frame_rate,
                "bit_rate_mbps": (
                    round(int(bit_rate) / 1000000, 2) if bit_rate != "N/A" else "N/A"
                ),
                "has_audio": audio_stream is not None,
                "audio_codec": (
                    audio_stream.get("codec_name", "N/A") if audio_stream else "N/A"
                ),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    skill = VideoAnalyze()
    result = skill.execute(params)
    print(json.dumps(result, ensure_ascii=False))


def execute(params):
    skill = VideoAnalyze()
    return skill.execute(params)
