#!/usr/bin/env python3
"""Character Render - Character Render 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""角色渲染器 - 每次生成新文件"""
import os
import time

from PIL import Image, ImageDraw, ImageFont


class CharacterRenderSkill:
    name = "character_render"
    description = "渲染角色形象"
    version = "1.0.0"
    category = "image"

    def execute(self, params):
        name = params.get("name", "角色")

        os.makedirs("output/characters", exist_ok=True)

        # 使用时间戳确保文件名唯一
        timestamp = int(time.time() * 1000)
        output_path = f"output/characters/{name}_{timestamp}.png"

        try:
            # 创建图片
            img = Image.new("RGB", (400, 400), color=(100, 80, 160))
            draw = ImageDraw.Draw(img)

            # 圆形背景
            draw.ellipse((50, 50, 350, 350), fill=(180, 130, 100))
            draw.ellipse((70, 70, 330, 330), fill=(220, 180, 140))

            # 眼睛
            draw.ellipse((150, 180, 190, 220), fill=(0, 0, 0))
            draw.ellipse((210, 180, 250, 220), fill=(0, 0, 0))
            draw.ellipse((160, 190, 180, 210), fill=(255, 255, 255))
            draw.ellipse((220, 190, 240, 210), fill=(255, 255, 255))

            # 嘴巴
            draw.arc((170, 240, 230, 280), 0, 180, fill=(0, 0, 0), width=3)

            # 中文字体
            font = None
            font_paths = [
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            ]
            for fp in font_paths:
                if os.path.exists(fp):
                    font = ImageFont.truetype(fp, 36)
                    break

            if font is None:
                font = ImageFont.load_default()

            # 绘制文字
            text = name[:2] if len(name) > 2 else name
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            draw.text(
                ((400 - text_width) // 2, 340), text, fill=(255, 255, 255), font=font
            )

            img.save(output_path, "PNG")

            return {
                "success": True,
                "character": name,
                "image_path": output_path,
                "size_bytes": os.path.getsize(output_path),
                "message": f"角色图片已生成: {output_path}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


skill = CharacterRenderSkill()
