#!/usr/bin/env python3
"""视频理解 - 提取视频多模态信息"""

import json
import subprocess
import sys
from pathlib import Path


class VideoUnderstanding:
    """视频理解类"""

    name = "video-understanding"
    description = "视频理解 - 提取多模态信息"
    version = "1.0.0"

    def execute(self, params):
        video_path = params.get("video_path", "")
        extract_subs = params.get("extract_subs", True)

        if not video_path:
            return {"success": False, "error": "请提供视频文件路径"}

        path = Path(video_path)
        if not path.exists():
            return {"success": False, "error": f"文件不存在: {video_path}"}

        result = {
            "success": True,
            "metadata": self._get_metadata(path),
            "transcription": self._transcribe_audio(path) if extract_subs else "",
            "summary": "",
            "topics": [],
        }

        # 生成摘要
        result["summary"] = self._generate_summary(result["metadata"], path.name)

        return result

    def _get_metadata(self, path):
        """获取视频元数据"""
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
        try:
            output = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(output.stdout)

            video_stream = None
            for s in data.get("streams", []):
                if s.get("codec_type") == "video":
                    video_stream = s
                    break

            size_mb = round(path.stat().st_size / 1024 / 1024, 2)
            duration = float(data.get("format", {}).get("duration", 0))

            return {
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
            }
        except Exception as e:
            return {"error": str(e)}

    def _transcribe_audio(self, path):
        """提取音频并转文字"""
        # TODO: 集成 whisper
        return "语音转文字功能待实现"

    def _generate_summary(self, metadata, filename):
        """生成视频摘要"""
        duration = metadata.get("duration_formatted", "未知")
        resolution = metadata.get("resolution", "未知")
        size = metadata.get("size_mb", 0)

        return f"分辨率 {resolution}，时长 {duration}，大小 {size:.1f}MB"


if __name__ == "__main__":
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    skill = VideoUnderstanding()
    result = skill.execute(params)
    print(json.dumps(result, ensure_ascii=False))
