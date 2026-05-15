"""FFmpeg 视频合成原子技能（增强版）"""
import subprocess
import os
from pathlib import Path

class FFmpegVideoSkill:
    name = "ffmpeg_video"
    description = "用 FFmpeg 将音频+背景图/纯色背景合成视频，支持字幕"
    version = "2.0.0"
    category = "video"

    def execute(self, params):
        audio_path = params.get("audio_path")
        output_path = params.get("output_path", "output/video.mp4")
        duration = params.get("duration", 180)
        
        # 背景：可以是图片路径或纯色
        background = params.get("background")  # 图片路径 或 颜色名(black/blue/white)
        bg_color = params.get("bg_color", "black")
        bg_image = params.get("bg_image")  # 优先使用图片
        
        # 字幕
        subtitle_text = params.get("subtitle_text", "")
        subtitle_position = params.get("subtitle_position", "bottom")
        
        width = params.get("width", 1920)
        height = params.get("height", 1080)
        
        if not audio_path or not os.path.exists(audio_path):
            return {"success": False, "error": "音频文件不存在"}
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 构建 ffmpeg 命令
        if bg_image and os.path.exists(bg_image):
            # 使用图片背景（循环播放）
            video_input = f"loop=1 -i {bg_image}"
            video_filter = f"scale={width}:{height}:force_original_aspect_ratio=1,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
        else:
            # 使用纯色背景
            video_input = f"-f lavfi -i color=c={bg_color}:s={width}x{height}:d={duration}"
            video_filter = "null"
        
        # 字幕滤镜
        if subtitle_text:
            # 转义特殊字符
            subtitle_text = subtitle_text.replace("'", "'\\''")
            drawtext = f"drawtext=text='{subtitle_text}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y={height-100}"
            if video_filter == "null":
                video_filter = drawtext
            else:
                video_filter = f"{video_filter},{drawtext}"
        
        # 构建完整命令
        cmd = ['ffmpeg', '-y']
        
        if bg_image:
            cmd.extend(['-stream_loop', '-1', '-i', bg_image])
            cmd.extend(['-i', audio_path])
            cmd.extend(['-filter_complex', f"[0:v]{video_filter}[v]; [v]fps=25[vout]"])
            cmd.extend(['-map', '[vout]', '-map', '1:a'])
        else:
            cmd.extend(video_input.split())
            cmd.extend(['-i', audio_path])
            if video_filter != "null":
                cmd.extend(['-vf', video_filter])
        
        cmd.extend(['-c:v', 'libx264', '-c:a', 'aac', '-shortest', '-pix_fmt', 'yuv420p', output_path])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0 and os.path.exists(output_path):
                return {
                    "success": True,
                    "output_path": output_path,
                    "size_bytes": os.path.getsize(output_path),
                    "duration": duration,
                    "has_subtitle": bool(subtitle_text)
                }
            else:
                return {"success": False, "error": result.stderr[:300]}
        except Exception as e:
            return {"success": False, "error": str(e)}

skill = FFmpegVideoSkill()
