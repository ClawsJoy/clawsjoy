#!/usr/bin/env python3
"""Avatar Maker Skill - Avatar Maker Skill 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""头像制作技能 - 从社区下载"""
from PIL import Image, ImageDraw, ImageFont
import os
import requests
from io import BytesIO

class AvatarMakerSkill:
    name = "avatar_maker"
    description = "制作卡通头像"
    version = "1.0.0"
    category = "image"
    
    def execute(self, params):
        text = params.get("text", "ClawsJoy")
        size = params.get("size", 200)
        
        # 创建头像
        img = Image.new('RGB', (size, size), color=(124, 58, 237))
        draw = ImageDraw.Draw(img)
        
        # 绘制文字
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size//4)
        except:
            font = ImageFont.load_default()
        
        # 获取文字边界框
        bbox = draw.textbbox((0, 0), text[:2], font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), text[:2], fill=(255, 255, 255), font=font)
        
        # 保存
        output_path = f"output/avatar_{hash(text) % 10000}.png"
        os.makedirs("output", exist_ok=True)
        img.save(output_path)
        
        return {
            "success": True,
            "avatar_path": output_path,
            "size": size,
            "text": text
        }

skill = AvatarMakerSkill()
