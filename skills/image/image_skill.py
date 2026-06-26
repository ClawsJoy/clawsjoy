"""图像处理"""
from PIL import Image
import os

class image_skill:
    name = "image"
    description = "图像处理"
    version = "1.0.0"
    
    def execute(self, params):
        path = params.get("path", "")
        action = params.get("action", "info")
        if action == "info" and os.path.exists(path):
            img = Image.open(path)
            return {"success": True, "width": img.width, "height": img.height, "format": img.format}
        elif action == "resize":
            img = Image.open(path)
            w, h = params.get("width", 512), params.get("height", 512)
            img.resize((w, h)).save(params.get("output", path))
            return {"success": True}
        return {"success": False, "error": "不支持"}
