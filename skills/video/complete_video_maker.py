#!/usr/bin/env python3
"""Complete Video Maker - Complete Video Maker 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import subprocess
import os
from pathlib import Path
from lib.file_utils import file_utils

class CompleteVideoMakerSkill:
    def execute(self, params):
        images = params.get('images', [])
        audio = params.get('audio', '')
        duration = params.get('duration', 3)
        title = params.get('title', 'ClawsJoy Video')
        
        output_path = file_utils.get_output_dir() / file_utils.generate_filename("complete", "mp4")
        
        # 如果没有图片，生成带文字的测试视频
        if not images:
            cmd = [
                "ffmpeg", "-f", "lavfi", "-i", 
                f"color=c=blue:s=640x480:d={duration}",
                "-vf", f"drawtext=text='{title}':fontsize=30:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
                "-y", str(output_path)
            ]
        else:
            # 有图片时，用图片合成
            cmd = ["ffmpeg"]
            for img in images:
                cmd.extend(["-loop", "1", "-i", img])
            cmd.extend([
                "-filter_complex", f"concat=n={len(images)}:v=1:a=0",
                "-t", str(duration), "-y", str(output_path)
            ])
        
        print(f"执行: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000:
                return {
                    "success": True,
                    "message": f"视频已合成，时长 {duration} 秒",
                    "file_path": str(output_path),
                    "size": output_path.stat().st_size,
                    "duration": duration
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr[:300] if result.stderr else "未知错误",
                    "returncode": result.returncode
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

skill = CompleteVideoMakerSkill()
