#!/usr/bin/env python3
"""Image Quality Check - Image Quality Check 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""图片质量检查器"""
from pathlib import Path

from PIL import Image


class ImageQualityCheckSkill:
    name = "image_quality_check"
    description = "检查图片质量"
    version = "1.0.0"
    category = "image"

    def execute(self, params):
        image_path = params.get("image_path", "")

        if not image_path or not Path(image_path).exists():
            return {"success": False, "error": "图片不存在"}

        img = Image.open(image_path)
        width, height = img.size
        size_kb = Path(image_path).stat().st_size / 1024

        issues = []
        if width < 640 or height < 480:
            issues.append(f"分辨率太低: {width}x{height}")
        if size_kb < 10:
            issues.append(f"文件太小: {size_kb:.1f}KB")

        return {
            "success": len(issues) == 0,
            "width": width,
            "height": height,
            "size_kb": round(size_kb, 1),
            "issues": issues,
            "quality_score": max(0, 100 - len(issues) * 25),
        }


skill = ImageQualityCheckSkill()
