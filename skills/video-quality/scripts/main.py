#!/usr/bin/env python3
"""视频质量分析 - 使用 ffprobe 分析画面"""

import json
import subprocess
import sys
from pathlib import Path


class VideoQuality:
    name = "video-quality"
    description = "分析视频画面质量"
    version = "1.0.0"

    def execute(self, params):
        video_path = params.get("video_path", "")
        if not video_path:
            return {"success": False, "error": "请提供视频文件路径"}

        path = Path(video_path)
        if not path.exists():
            return {"success": False, "error": f"文件不存在: {video_path}"}

        # 获取视频流信息
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-select_streams",
            "v:0",
            "-show_streams",
            str(path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return {"success": False, "error": "分析失败"}

        data = json.loads(result.stdout)
        stream = data.get("streams", [{}])[0]

        width = stream.get("width", 0)
        height = stream.get("height", 0)

        # 判断画质等级
        pixels = width * height
        if pixels >= 3840 * 2160:
            quality = "4K (Ultra HD)"
        elif pixels >= 1920 * 1080:
            quality = "1080p (Full HD)"
        elif pixels >= 1280 * 720:
            quality = "720p (HD)"
        elif pixels >= 640 * 480:
            quality = "480p (SD)"
        else:
            quality = "低清"

        # 判断比例
        if width > 0 and height > 0:
            ratio = round(width / height, 2)
            if ratio > 1.7:
                aspect = "宽屏 (16:9)"
            elif ratio > 1.3:
                aspect = "标准 (4:3)"
            else:
                aspect = "竖屏"
        else:
            aspect = "未知"

        return {
            "success": True,
            "file_name": path.name,
            "resolution": f"{width}x{height}",
            "quality": quality,
            "aspect_ratio": aspect,
            "codec": stream.get("codec_name", "N/A"),
            "bitrate": stream.get("bit_rate", "N/A"),
            "frame_rate": stream.get("r_frame_rate", "N/A"),
        }


if __name__ == "__main__":
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    skill = VideoQuality()
    result = skill.execute(params)
    print(json.dumps(result))


def execute(params):
    skill = VideoQuality()
    return skill.execute(params)
