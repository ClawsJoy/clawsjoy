"""图像识别技能 - 使用 llava:7b 模型"""

import base64
import requests
from pathlib import Path


class VisionSkill:
    """图像识别技能类"""
    
    def execute(self, params: dict) -> dict:
        """执行图像识别"""
        image_path = params.get('image_path', '')
        prompt = params.get('prompt', '描述这张图片的内容')
        
        if not image_path:
            return {"success": False, "error": "image_path is required"}
        
        path = Path(image_path)
        if not path.exists():
            return {"success": False, "error": f"Image file not found: {image_path}"}
        
        # 读取并编码图片
        with open(path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode()
        
        # 调用 Ollama llava
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llava:7b",
                    "prompt": prompt,
                    "images": [image_base64],
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "result": result.get('response', ''),
                    "image": str(path)
                }
            else:
                return {"success": False, "error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# 全局实例（技能加载器需要）
skill = VisionSkill()
