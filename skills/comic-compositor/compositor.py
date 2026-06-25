"""漫剧分镜合成器 - 纯 Python 实现"""

from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path
import json

class ComicCompositor:
    def __init__(self, asset_root="data/assets/novels/AI觉醒"):
        self.root = Path(asset_root)
    
    def composite(self, scene_path, character_path, position, scale=1.0, 
                  brightness=1.0, shadow=False, output_path=None):
        """合成单帧分镜
        
        Args:
            scene_path: 场景底图路径
            character_path: 角色图路径
            position: (x, y) 角色放置位置（左上角）
            scale: 角色缩放比例
            brightness: 角色亮度调整（<1 变暗，>1 变亮）
            shadow: 是否添加阴影
            output_path: 输出路径
        """
        scene = Image.open(scene_path).convert('RGBA')
        character = Image.open(character_path).convert('RGBA')
        
        # 缩放角色
        new_size = (int(character.width * scale), int(character.height * scale))
        character = character.resize(new_size, Image.LANCZOS)
        
        # 调整亮度
        enhancer = ImageEnhance.Brightness(character)
        character = enhancer.enhance(brightness)
        
        # 添加阴影
        if shadow:
            shadow_layer = Image.new('RGBA', character.size, (0, 0, 0, 80))
            character = Image.alpha_composite(character, shadow_layer)
        
        # 合成
        canvas = scene.copy()
        canvas.paste(character, position, character)
        
        # 保存
        output_path = output_path or f"{Path(scene_path).stem}_合成.png"
        canvas.save(output_path)
        return output_path

compositor = ComicCompositor()
