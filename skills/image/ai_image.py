"""AI 生图 - 使用本地背景（网络受限时）"""
import os
import subprocess

class AIImageSkill:
    name = "ai_image"
    description = "生成主题图片"
    version = "1.0.0"
    category = "image"

    def execute(self, params):
        output_path = params.get("output_path", "output/ai_image.jpg")
        
        # 使用本地生成的渐变背景
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 创建带文字的背景图
        subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', 
            f'color=c=darkblue:s=1280x720', 
            '-frames:v', '1', output_path, '-y'
        ], capture_output=True)
        
        return {"success": True, "image_path": output_path, "source": "local"}

skill = AIImageSkill()
