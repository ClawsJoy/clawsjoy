"""视频状态检查"""
import subprocess, json

class check_video_status_skill:
    name = "check-video-status"
    description = "检查视频文件状态"
    version = "1.0.0"
    
    def execute(self, params):
        path = params.get("path", "")
        if not os.path.exists(path):
            return {"success": False, "error": "文件不存在"}
        result = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', path],
                              capture_output=True, text=True)
        info = json.loads(result.stdout)['format']
        return {"success": True, "duration": float(info['duration']), "size": int(info['size'])}
