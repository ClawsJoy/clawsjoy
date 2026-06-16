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
    version = "1.0.0"

    def __init__(self):
        self.download_path = Path(os.path.expanduser("~/Downloads/youtube"))
        self.download_path.mkdir(parents=True, exist_ok=True)

    def execute(self, params: dict) -> dict:
        """执行下载
        
        params:
            url: YouTube 视频链接 (必需)
            quality: 画质 (best/1080p/720p/audio)
            get_info: 是否只获取信息 (True/False)
        """
        url = params.get("url", "")
        quality = params.get("quality", "best")
        get_info = params.get("get_info", False)

        if not url:
            return {"success": False, "error": "请提供 YouTube 链接"}

        # 提取 URL
        url = self._extract_url(url)
        if not url:
            return {"success": False, "error": "无效的 YouTube 链接"}

        # 检查 yt-dlp 是否安装
        if not self._check_yt_dlp():
            return {
                "success": False,
                "error": "yt-dlp 未安装，请运行: pip install yt-dlp"
            }

        # 只获取信息
        if get_info:
            return self._get_info(url)

        # 下载视频
        return self._download(url, quality)

    def _extract_url(self, text: str) -> str:
        """从文本中提取 YouTube URL"""
        pattern = r'https?://(?:www\.)?(?:youtu\.be/|youtube\.com/watch\?v=)[^\s]+'
        match = re.search(pattern, text)
        return match.group(0) if match else ""

    def _check_yt_dlp(self) -> bool:
        """检查 yt-dlp 是否安装"""
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, timeout=5)
            return True
        except:
            return False

    def _get_info(self, url: str) -> dict:
        """获取视频信息"""
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
        """下载视频"""
        try:
            # 构建命令
            if quality == "audio":
                cmd = [
                    "yt-dlp", "-x", "--audio-format", "mp3",
                    "-o", f"{self.download_path}/%(title)s.%(ext)s",
                    url
                ]
            else:
                format_str = "bestvideo+bestaudio" if quality == "best" else f"bestvideo[height<={quality}]+bestaudio"
                cmd = [
                    "yt-dlp",
                    "-f", format_str,
                    "--merge-output-format", "mp4",
                    "-o", f"{self.download_path}/%(title)s.%(ext)s",
                    url
                ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode != 0:
                return {"success": False, "error": result.stderr}

            return {
                "success": True,
                "message": f"下载完成，保存到: {self.download_path}",
                "path": str(self.download_path)
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "下载超时（超过10分钟）"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_info(self, url: str) -> dict:
        """获取视频信息（公开方法）"""
        return self._get_info(url)


# 全局实例
downloader = video_download()
