"""图像识别技能 - 使用 Ollama LLaVA 模型"""

import requests
import base64

def execute(params: dict) -> dict:
    """识别图像内容"""
    image_path = params.get('image_path', '')
    question = params.get('question', '描述这张图片的内容')
    
    if not image_path:
        return {"success": False, "error": "image_path required"}
    
    # 读取并编码图像
    with open(image_path, 'rb') as f:
        image_base64 = base64.b64encode(f.read()).decode()
    
    # 调用 Ollama LLaVA
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llava:7b",
            "prompt": question,
            "images": [image_base64],
            "stream": False
        }
    )
    
    if response.status_code == 200:
        return {
            "success": True,
            "description": response.json().get('response', ''),
            "image": image_path
        }
    
    return {"success": False, "error": "识别失败"}
