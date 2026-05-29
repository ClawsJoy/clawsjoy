"""FFmpeg 视频处理 - 真实执行"""
import subprocess
import os
from pathlib import Path

class FfmpegVideoSkill:
    def execute(self, params):
        output_path = params.get('output', '')
        if not output_path:
            return {"success": False, "error": "缺少输出路径"}
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 构建命令
        cmd = ["ffmpeg", "-f", "lavfi", "-i", "color=c=blue:s=1920x1080:d=5", "-y", output_path]
        
        print(f"执行: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and os.path.exists(output_path):
                return {
                    "success": True,
                    "message": "视频已生成",
                    "output": output_path,
                    "size": os.path.getsize(output_path)
                }
            else:
                return {"success": False, "error": result.stderr[:200]}
        except Exception as e:
            return {"success": False, "error": str(e)}

skill = FfmpegVideoSkill()
