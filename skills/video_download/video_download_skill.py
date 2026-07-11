#!/usr/bin/env python3
"""video-download 技能 - 下载 YouTube 视频"""

import subprocess
import json
import re
import os
from pathlib import Path


class video_download:
    name = "video-download"
    description = "下载 YouTube 视频到本地"
    version = "1.1.0"

    def __init__(self):
        self.download_path = Path(os.path.expanduser("~/Downloads/youtube"))
        self.download_path.mkdir(parents=True, exist_ok=True)

    def execute(self, params: dict) -> dict:
        url = params.get("url", "")
        quality = params.get("quality", "720p")  # 默认 720p
        get_info = params.get("get_info", False)

        if not url:
            return {"success": False, "error": "请提供 YouTube 链接"}

        url = self._extract_url(url)
        if not url:
            return {"success": False, "error": "无效的 YouTube 链接"}

        if not self._check_yt_dlp():
            return {"success": False, "error": "yt-dlp 未安装，请运行: pip install yt-dlp"}

        if get_info:
            return self._get_info(url)

        return self._download(url, quality)

    def _extract_url(self, text: str) -> str:
        pattern = r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|shorts/))[^\s]+'
        match = re.search(pattern, text)
        return match.group(0) if match else ""

    def _check_yt_dlp(self) -> bool:
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, timeout=5)
            return True
        except:
            return False

    def _get_info(self, url: str) -> dict:
        try:
            result = subprocess.run(
                ["yt-dlp", "--dump-json", url],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                return {"success": False, "error": result.stderr}

            info = json.loads(result.stdout)
            return {
                "success": True,
                "title": info.get("title", "未知"),
                "uploader": info.get("uploader", "未知"),
                "duration": info.get("duration", 0),
                "view_count": info.get("view_count", 0),
                "formats": len(info.get("formats", [])),
                "thumbnail": info.get("thumbnail", "")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _download(self, url: str, quality: str) -> dict:
        """
        下载视频 - 使用最佳音视频合并
        quality: 720p, 1080p, best, audio
        """
        try:
            # 质量映射
            quality_map = {
                "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
                "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                "best": "bestvideo+bestaudio/best",
                "audio": "bestaudio"
            }
            format_str = quality_map.get(quality, quality_map["720p"])

            # 构建命令
            # 自动检测 cookies 文件
            cookies_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents", "youtube_agent", "cookies.txt")
            if not os.path.exists(cookies_file):
                cookies_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
            
            if quality == "audio":
                cmd = [
                    "yt-dlp",
                    "-f", "bestaudio",
                    "--extract-audio",
                    "--audio-format", "mp3",
                    "--audio-quality", "0",
                    "-o", f"{self.download_path}/%(title)s.%(ext)s",
                    url
                ]
            else:
                cmd = [
                    "yt-dlp",
                    "-f", format_str,
                    "--merge-output-format", "mp4",
                    "-o", f"{self.download_path}/%(title)s.%(ext)s",
                    url
                ]

            if os.path.exists(cookies_file):
                cmd.insert(1, cookies_file)
                cmd.insert(1, "--cookies")
            print(f"[video_download] 执行: {' '.join(cmd[:4])}...")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode != 0:
                return {"success": False, "error": result.stderr}

            return {
                "success": True,
                "message": f"✅ 下载完成，保存到: {self.download_path}",
                "path": str(self.download_path),
                "quality": quality
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "下载超时（超过10分钟）"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# 全局实例
downloader = video_download()
