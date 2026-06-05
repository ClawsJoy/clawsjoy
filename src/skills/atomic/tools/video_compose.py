#!/usr/bin/env python3
"""Video Compose - Video Compose 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import sys

from lib.smart_config import smart_config

sys.path.insert(0, "str(smart_config.ROOT)")
import hashlib
import os
import subprocess


class VideoComposeSkill:
    name = "video_compose"
    description = "合成视频"
    version = "1.0.0"
    category = "tools"

    def execute(self, params):
        image_path = params.get("image_path", "")
        audio_path = params.get("audio_path", "")
        duration = params.get("duration", 30)

        os.makedirs("output", exist_ok=True)

        if not image_path:
            # 如果没有图片，生成默认背景
            image_path = "output/default_bg.png"
            from PIL import Image

            img = Image.new("RGB", (800, 600), color=(50, 50, 100))
            img.save(image_path)

        output_path = (
            f"output/video_{hashlib.md5(str(params).encode()).hexdigest()[:8]}.mp4"
        )

        if audio_path and os.path.exists(audio_path):
            cmd = [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-i",
                image_path,
                "-i",
                audio_path,
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                "-t",
                str(duration),
                output_path,
            ]
        else:
            cmd = [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"testsrc=duration={duration}:size=800x600:rate=1",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-preset",
                "ultrafast",
                output_path,
            ]

        result = subprocess.run(cmd, capture_output=True)

        if result.returncode == 0 and os.path.exists(output_path):
            return {
                "success": True,
                "video_path": output_path,
                "duration": duration,
                "size": os.path.getsize(output_path),
                "message": f"视频已生成: {output_path}",
            }
        else:
            return {
                "success": False,
                "error": result.stderr[:200],
                "message": "视频合成失败",
            }


skill = VideoComposeSkill()
