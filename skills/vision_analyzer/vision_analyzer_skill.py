#!/usr/bin/env python3
"""视觉分析技能 - 使用 Ollama llava"""

import requests
import base64
from pathlib import Path


class VisionAnalyzerSkill:
    name = "vision_analyzer"
    description = "图像分析"
    version = "1.0.0"

    def __init__(self):
        self.llm_url = "http://localhost:11434/api/generate"
        self.model = "llava"

    def analyze(self, image_path: str, prompt: str = "描述这张图片") -> dict:
        """分析图像"""
        if not Path(image_path).exists():
            return {"success": False, "error": f"图像不存在: {image_path}"}

        try:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
        except Exception as e:
            return {"success": False, "error": f"读取图像失败: {e}"}

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
            "options": {"temperature": 0.3}
        }

        try:
            resp = requests.post(self.llm_url, json=payload, timeout=60)
            if resp.status_code == 200:
                result = resp.json()
                return {
                    "success": True,
                    "description": result.get("response", "无法描述"),
                    "model": self.model
                }
            return {"success": False, "error": f"LLM 错误: {resp.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


def execute(params):
    skill = VisionAnalyzerSkill()
    return skill.analyze(params.get("image"), params.get("prompt", "描述这张图片"))
