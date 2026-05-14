from skills.skill_interface import BaseSkill
import requests
import urllib.parse
import uuid
from pathlib import Path
from datetime import datetime

class AiImageGenSkill(BaseSkill):
    name = "ai_image_gen"
    description = "AI 图片生成（支持 Pollinations API）"
    version = "1.0.0"
    category = "image"
    
    def execute(self, params):
        prompt = params.get("prompt", "")
        width = params.get("width", 1024)
        height = params.get("height", 768)
        
        if not prompt:
            return {"success": False, "error": "prompt is required"}
        
        IMAGE_DIR = Path("/mnt/d/clawsjoy/web/images/ai_generated")
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}"
        
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                IMAGE_DIR.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                img_name = f"{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
                img_path = IMAGE_DIR / img_name
                with open(img_path, 'wb') as f:
                    f.write(resp.content)
                return {"success": True, "image_path": str(img_path), "prompt": prompt}
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Generation failed"}

skill = AiImageGenSkill()
