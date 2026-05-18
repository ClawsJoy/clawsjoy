from lib.smart_config import smart_config
"""二维码生成"""
import qrcode
from PIL import Image
import os

class QRCodeGenSkill:
    name = "qrcode_gen"
    description = "生成二维码"
    version = "1.0.0"
    category = "image"
    
    def execute(self, params):
        data = params.get("data", "")
        size = params.get("size", 200)
        
        if not data:
            return {"success": False, "error": "需要提供数据"}
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        output_path = f"output/qrcode_{hash(data) % 10000}.png"
        os.makedirs("output", exist_ok=True)
        img.save(output_path)
        
        return {
            "success": True,
            "qrcode_path": output_path,
            "data": data,
            "size": size
        }

skill = QRCodeGenSkill()
