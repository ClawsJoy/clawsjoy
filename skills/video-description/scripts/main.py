#!/usr/bin/env python3
"""获取 YouTube 视频信息（含字幕）"""

import json
import subprocess
import sys


class VideoDescription:
    name = "video_description"
    description = "获取 YouTube 视频信息（含字幕）"
    version = "1.1.0"

    def execute(self, params):
        url = params.get("url", "")
        include_subs = params.get("include_subs", True)

        if not url:
            return {"success": False, "error": "请提供视频链接"}

        try:
            # 获取视频基本信息
            cmd_info = [
                "yt-dlp",
                "--skip-download",
                "--dump-json",
                "--no-warnings",
                url,
            ]
            result = subprocess.run(
                cmd_info, capture_output=True, text=True, timeout=30
            )

            if result.returncode != 0:
                return {"success": False, "error": "获取视频信息失败"}

            data = json.loads(result.stdout)

            response = {
                "success": True,
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "uploader": data.get("uploader", ""),
                "duration": data.get("duration", 0),
                "view_count": data.get("view_count", 0),
                "like_count": data.get("like_count", 0),
                "url": url,
            }

            # 获取字幕
            if include_subs:
                try:
                    # 获取自动生成的字幕
                    cmd_subs = [
                        "yt-dlp",
                        "--skip-download",
                        "--write-subs",
                        "--sub-lang",
                        "en,zh-Hans,zh-CN,zh-TW",
                        "--sub-format",
                        "vtt",
                        "--convert-subs",
                        "vtt",
                        "--no-warnings",
                        url,
                    ]
                    subprocess.run(cmd_subs, capture_output=True, text=True, timeout=30)

                    # 查找下载的字幕文件
                    import os
                    import re
                    from pathlib import Path

                    video_id = data.get("id", "")
                    sub_files = list(Path(".").glob(f"{video_id}*.vtt"))

                    if sub_files:
                        with open(sub_files[0], "r", encoding="utf-8") as f:
                            sub_content = f.read()
                        # 提取纯文本（去掉时间轴）
                        lines = sub_content.split("\n")
                        text_lines = []
                        for line in lines:
                            if (
                                not re.match(r"\d{2}:\d{2}:\d{2}", line)
                                and "-->" not in line
                                and line.strip()
                            ):
                                text_lines.append(line.strip())
                        response["subtitles"] = " ".join(text_lines)[:2000]  # 限制长度
                        # 清理临时字幕文件
                        for f in sub_files:
                            f.unlink()
                    else:
                        response["subtitles"] = "无可用字幕"
                except Exception as e:
                    response["subtitles"] = f"获取字幕失败: {str(e)}"

            return response

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "请求超时"}
        except Exception as e:
            return {"success": False, "error": f"获取失败: {str(e)}"}


if __name__ == "__main__":
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    skill = VideoDescription()
    result = skill.execute(params)
    print(json.dumps(result, ensure_ascii=False))
