"""多模态支持 - 图像识别、语音处理"""

import base64
from pathlib import Path
from typing import Optional


class ImageProcessor:
    """图像处理器"""
    
    def __init__(self):
        self.ollama_url = config_helper.get_llm_endpoint()
    
    def analyze(self, image_path: str, prompt: str = "描述这张图片") -> Optional[str]:
        """分析图片内容"""
        if not Path(image_path).exists():
            return "图片文件不存在"

        try:
            with open(image_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode()

            import requests
            resp = requests.post(f"{self.ollama_url}/api/generate",
                json={"model": "llava:7b", "prompt": prompt, "images": [img_data], "stream": False},
                timeout=config_helper.get_timeout("llm"))
            if resp.status_code == 200:
                return resp.json().get('response', '无法识别')
        except Exception as e:
            print(f"图像分析失败: {e}")

        return "图像分析服务不可用"
    
    def extract_text(self, image_path: str) -> Optional[str]:
        """OCR 文字识别"""
        return self.analyze(image_path, "请提取图片中的所有文字")


class AudioProcessor:
    """音频处理器"""
    
    def __init__(self):
        pass
    
    def text_to_speech(self, text: str, voice: str = "zh-CN") -> Optional[bytes]:
        """文字转语音"""
        # 需要配置 TTS 服务
        print(f"TTS: {text[:50]}...")
        return None


image_processor = ImageProcessor()
audio_processor = AudioProcessor()
