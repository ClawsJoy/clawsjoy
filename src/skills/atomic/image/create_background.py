#!/usr/bin/env python3
"""Create Background - Create Background 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""创建背景图"""
import os

from PIL import Image, ImageDraw


class CreateBackgroundSkill:
    name = "create_background"
    description = "创建仙侠风格背景"
    version = "1.0.0"
    category = "image"

    def execute(self, params):
        os.makedirs("output/bg", exist_ok=True)
        output_path = "output/bg/xianxia_bg.png"

        # 创建渐变背景
        img = Image.new("RGB", (800, 600), color=(50, 40, 80))
        draw = ImageDraw.Draw(img)

        # 绘制云朵效果
        draw.ellipse((100, 100, 250, 200), fill=(180, 170, 220), outline=None)
        draw.ellipse((180, 80, 320, 180), fill=(190, 180, 230), outline=None)
        draw.ellipse((600, 80, 750, 180), fill=(180, 170, 220), outline=None)
        draw.ellipse((650, 120, 780, 200), fill=(190, 180, 230), outline=None)

        # 绘制远山
        draw.polygon([(0, 500), (100, 350), (200, 500)], fill=(80, 70, 110))
        draw.polygon([(150, 500), (300, 300), (450, 500)], fill=(70, 60, 100))
        draw.polygon([(400, 500), (550, 320), (700, 500)], fill=(85, 75, 115))

        img.save(output_path)
        return {"success": True, "background_path": output_path}


skill = CreateBackgroundSkill()
