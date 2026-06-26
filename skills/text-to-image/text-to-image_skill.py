"""文本处理"""
class text_to_image_skill:
    name = "text-to-image"
    description = "文本转图像描述"
    version = "1.0.0"
    
    def execute(self, params):
        text = params.get("text", "")
        return {"success": True, "message": "请使用 DreamShaper 或豆包生成图像", "prompt": text}
