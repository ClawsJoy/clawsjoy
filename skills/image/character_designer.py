"""角色设计器 - 简化版（不抠图）"""
import os
from PIL import Image, ImageDraw, ImageFont

class CharacterDesignerSkill:
    name = "character_designer"
    description = "生成角色形象"
    version = "1.0.0"
    category = "image"

    def create_character(self, params):
        name = params.get("name", "主角")
        
        os.makedirs('output/characters', exist_ok=True)
        img_path = f"output/characters/{name}.png"
        
        # 生成圆形头像
        img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 画圆形背景
        draw.ellipse((0, 0, 200, 200), fill='#3498db')
        
        # 添加文字
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 60)
        except:
            font = ImageFont.load_default()
        
        draw.text((70, 70), name[:2], fill='white', font=font)
        img.save(img_path)
        
        return {"success": True, "character": name, "image": img_path}
    
    def get_character(self, name):
        path = f"output/characters/{name}.png"
        return path if os.path.exists(path) else None

skill = CharacterDesignerSkill()
