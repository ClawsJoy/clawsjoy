#!/usr/bin/env python3
"""视觉识别技能 - 使用 moondream 模型"""

import base64
import json
import sys
from pathlib import Path

from core.lib.llm_client import llm_client


class VisionSkill:
    name = "vision"
    description = "图像识别技能"
    version = "1.0.0"

    def execute(self, params):
        image_path = params.get("image_path", "")
        prompt = params.get("prompt", "描述这张图片")

        if not image_path:
            return {"success": False, "error": "请提供图片路径"}

        path = Path(image_path)
        if not path.exists():
            return {"success": False, "error": f"图片不存在: {image_path}"}

        # 读取图片并转为 base64
        with open(path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()

        # 调用 Ollama 视觉模型
        try:
            response = llm_client.generate(prompt=prompt, model="moondream:1.8b", max_tokens=512, temperature=0.7, task_type="skill")

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "result": result.get("response", "无响应"),
                    "image": image_path,
                    "prompt": prompt,
                }
            else:
                return {"success": False, "error": f"API错误: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


def execute(params):
    """统一执行入口"""
    skill = VisionSkill()
    return skill.execute(params)


if __name__ == "__main__":
    # 测试
    result = execute(
        {"image_path": "downloads/image_20260607_081900.png", "prompt": "描述这张图片"}
    )
    print(json.dumps(result, ensure_ascii=False))
