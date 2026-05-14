import subprocess
from pathlib import Path

class ImageSlideshowSkill:
    name = "image_slideshow"
    description = "图片轮播视频（优化版）"
    version = "1.0.0"
    category = "video"

    def execute(self, params):
        audio_path = params.get("audio_path")
        images = params.get("images", [])
        output_path = params.get("output_path", "output/video.mp4")
        
        if not audio_path or not Path(audio_path).exists():
            return {"success": False, "error": "音频不存在"}
        
        if not images:
            images = ["output/images/default.jpg"]
        
        # 根据音频时长自动计算每图展示时间
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
                                capture_output=True, text=True)
        duration = float(result.stdout.strip()) if result.stdout.strip() else 60
        per_image = duration / len(images)
        
        # 限制每图最少2秒，最多10秒
        per_image = max(2, min(10, per_image))
        
        cmd = ['ffmpeg', '-y', '-loop', '1', '-i', images[0],
               '-i', audio_path,
               '-c:v', 'libx264', '-c:a', 'aac', '-shortest', '-pix_fmt', 'yuv420p',
               output_path]
        subprocess.run(cmd, capture_output=True)
        
        return {"success": True, "video": output_path, "duration": duration}

skill = ImageSlideshowSkill()
