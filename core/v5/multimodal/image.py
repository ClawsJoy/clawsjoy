#!/usr/bin/env python3
"""Image - Image 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


import base64
from pathlib import Path
from typing import Dict, Optional

import requests


class ImageProcessor:
    """图像处理器"""

    def __init__(self):
        self.ollama_url = config_helper.get_llm_endpoint()

    def analyze_image(
        self, image_path: str, prompt: str = "描述这张图片"
    ) -> Optional[str]:
        """分析图片内容"""
        if not Path(image_path).exists():
            return None

        # 读取并编码图片
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()

        try:
            # 使用 LLaVA 或其他多模态模型
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llava:7b",
                    "prompt": prompt,
                    "images": [image_data],
                    "stream": False,
                },
                timeout=config_helper.get_timeout("llm"),
            )

            if response.status_code == 200:
                return response.json().get("response", "无法识别图片内容")
        except Exception as e:
            print(f"图像分析失败: {e}")

        return "图像分析服务不可用"

    def extract_text(self, image_path: str) -> Optional[str]:
        """OCR 文字识别"""
        return self.analyze_image(image_path, "请提取图片中的所有文字")


image_processor = ImageProcessor()
