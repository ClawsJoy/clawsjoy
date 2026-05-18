"""漫剧视频制作技能 - 修复版"""
import os
import subprocess
import hashlib

class ManjuMakerSkill:
    name = "manju_maker"
    description = "一键生成漫剧视频"
    version = "3.0.0"
    category = "video"

    def execute(self, params):
        topic = params.get("topic", "")
        if not topic:
            return {"success": False, "error": "需要提供主题"}

        print(f"🎬 制作漫剧: {topic}")

        os.makedirs("output", exist_ok=True)
        
        # 生成唯一文件名
        topic_hash = abs(hash(topic)) % 10000
        output_path = f"output/manju_{topic_hash}.mp4"
        
        # 使用 ffmpeg 生成带文字的测试视频
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=blue:s=1280x720:d=10",
            "-vf", f"drawtext=text='{topic}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
            "-c:v", "libx264", "-t", "10", output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path):
            size = os.path.getsize(output_path)
            return {
                "success": True,
                "video": output_path,
                "size_kb": size // 1024,
                "duration": 10,
                "message": f"视频已生成: {output_path}"
            }
        
        return {"success": False, "error": f"视频生成失败: {result.stderr[:200]}"}

skill = ManjuMakerSkill()
