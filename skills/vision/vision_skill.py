#!/usr/bin/env python3
"""图像识别技能，使用 moondream 模型识别图片内容"""

import base64
from pathlib import Path

import requests


class VisionSkill:
    """图像识别技能类"""

    # ========== 必需属性 ==========
    name = "vision"
    description = "图像识别技能，使用 moondream 模型识别图片内容"
    version = "1.0.0"
    category = "image"

    def execute(self, params: dict) -> dict:
        """执行图像识别

        Args:
            params:
                - image_path: 图片文件路径 (必需)
                - prompt: 识别提示词 (可选，默认为描述图片)

        Returns:
            {"success": True, "result": "描述内容", "image": "路径"}
            {"success": False, "error": "错误信息"}
        """
        image_path = params.get("image_path", "")
        prompt = params.get("prompt", "描述这张图片的内容")

        if not image_path:
            return {"success": False, "error": "image_path is required"}

        path = Path(image_path)
        if not path.exists():
            return {"success": False, "error": f"Image file not found: {image_path}"}

        # 读取并编码图片
        with open(path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()

        # 调用 Ollama moondream
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "moondream:1.8b",
                    "prompt": prompt,
                    "images": [image_base64],
                    "stream": False,
                },
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "result": result.get("response", ""),
                    "image": str(path),
                }
            else:
                return {
                    "success": False,
                    "error": f"Ollama API error: {response.status_code}",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}


# 全局实例（技能加载器需要）
skill = VisionSkill()
