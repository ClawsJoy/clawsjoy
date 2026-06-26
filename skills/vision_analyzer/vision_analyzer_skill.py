"""图像分析 - 使用llava"""
import base64, requests, os

class vision_analyzer:
    name = "vision_analyzer"
    description = "使用Ollama llava分析图像"
    version = "1.0.0"

    def execute(self, params):
        path = params.get("path", "")
        if not path or not os.path.exists(path):
            return {"success": False, "error": "请提供有效的图片路径"}
        try:
            with open(path, 'rb') as fp:
                img = base64.b64encode(fp.read()).decode()
            r = requests.post('http://localhost:11434/api/generate', json={
                'model': 'llava:latest',
                'prompt': params.get("question", "描述图片"),
                'images': [img], 'stream': False
            }, timeout=30)
            return {"success": True, "description": r.json().get('response', '')}
        except Exception as e:
            return {"success": False, "error": str(e)}
