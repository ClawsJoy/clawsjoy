#!/usr/bin/env python3
"""视觉分析技能 - 基于统一LLM客户端"""

import base64
from pathlib import Path
from core.lib.llm_client import llm_client


class VisionAnalyzerSkill:
    name = "vision_analyzer"
    description = "图像分析"
    version = "1.1.0"

    def __init__(self):
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

        return llm_client.generate_multimodal(
            prompt=prompt,
            model=self.model,
            images=[image_data],
            temperature=0.3,
            max_tokens=512,
            timeout=60,
            task_type="vision"
        )


def execute(params):
    skill = VisionAnalyzerSkill()
    return skill.analyze(params.get("image"), params.get("prompt", "描述这张图片"))
