"""视频修剪"""
import subprocess, os

class video_trim_skill:
    name = "video-trim"
    description = "视频裁剪"
    version = "1.0.0"
    
    def execute(self, params):
        path = params.get("path", "")
        start = params.get("start", 0)
        duration = params.get("duration", 10)
        output = params.get("output", path.replace(".mp4", "_trimmed.mp4"))
        subprocess.run(['ffmpeg', '-y', '-i', path, '-ss', str(start), '-t', str(duration),
                      '-c', 'copy', output], capture_output=True)
        return {"success": True, "output": output}
