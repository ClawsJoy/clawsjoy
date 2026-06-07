#!/usr/bin/env python3
"""视频下载技能"""

import json
import re
import subprocess
import sys
from pathlib import Path


class VideoDownloadSkill:
    name = "video-download"
    description = "下载 YouTube 视频"
    version = "1.0.0"

    def execute(self, params):
        url = params.get("url", "")
        if not url:
            return {"success": False, "error": "请提供 URL"}

        output_dir = Path("./downloads")
        output_dir.mkdir(exist_ok=True)

        cmd = ["yt-dlp", "-f", "best", "-o", f"{output_dir}/%(title)s.%(ext)s", url]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return {"success": True, "result": "下载成功", "url": url}
        return {"success": False, "error": result.stderr[:200]}


def execute(params):
    skill = VideoDownloadSkill()
    return skill.execute(params)
