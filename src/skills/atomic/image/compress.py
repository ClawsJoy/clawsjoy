#!/usr/bin/env python3
"""Compress - Compress 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""图片压缩技能"""
import os

from PIL import Image


class CompressSkill:
    name = "compress"
    description = "图片压缩"
    version = "1.0.0"
    category = "image"

    def execute(self, params):
        image_path = params.get("image_path", "")
        quality = params.get("quality", 80)

        if not image_path or not os.path.exists(image_path):
            return {"success": False, "error": "图片不存在"}

        output_path = image_path.replace(".", f"_compressed.")
        img = Image.open(image_path)
        img.save(output_path, quality=quality, optimize=True)

        return {"success": True, "output_path": output_path, "quality": quality}


skill = CompressSkill()
