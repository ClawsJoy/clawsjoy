"""漫剧分镜合成器 v2.0 - 批量自动化"""

from PIL import Image, ImageEnhance
from rembg import remove
from pathlib import Path
import json

class ComicCompositor:
    def __init__(self, asset_root="data/assets/novels/AI觉醒"):
        self.root = Path(asset_root)
        self.characters_dir = self.root / "characters"
        self.scenes_dir = self.root / "scenes"
        self.output_dir = self.root / "storyboard"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_character(self, name, version="道具"):
        """加载角色图并去背景"""
        char_dir = self.characters_dir / name / "images"
        # 找对应版本的文件
        for f in char_dir.glob(f"*{version}*"):
            if f.suffix == '.png' and ':Zone' not in f.name:
                raw = Image.open(f).convert('RGBA')
                return remove(raw)
        # fallback: 任意一张
        for f in char_dir.glob("*.png"):
            if ':Zone' not in f.name:
                raw = Image.open(f).convert('RGBA')
                return remove(raw)
        raise FileNotFoundError(f"未找到 {name} 的角色图")
    
    def load_scene(self, name):
        """加载场景底图"""
        for f in self.scenes_dir.glob(f"*{name}*"):
            if f.suffix == '.png':
                return Image.open(f).convert('RGBA')
        raise FileNotFoundError(f"未找到场景: {name}")
    
    def composite(self, scene_name, characters, output_name):
        """
        合成单帧分镜
        
        Args:
            scene_name: 场景文件名关键词
            characters: [{"name": "林浩", "scale": 0.25, "x": "right-60", "y": "bottom+10", "brightness": 0.7}]
            output_name: 输出文件名
        """
        scene = self.load_scene(scene_name)
        
        for cfg in characters:
            char = self.load_character(cfg["name"], cfg.get("version", "道具"))
            
            # 缩放
            s = cfg.get("scale", 0.25)
            char = char.resize((int(char.width*s), int(char.height*s)), Image.LANCZOS)
            
            # 亮度
            char = ImageEnhance.Brightness(char).enhance(cfg.get("brightness", 0.7))
            
            # 位置解析：支持 "right-60" "bottom+10" "center" 等
            x = self._parse_position(cfg.get("x", "right-60"), scene.width, char.width)
            y = self._parse_position(cfg.get("y", "bottom+10"), scene.height, char.height)
            
            scene.paste(char, (x, y), char)
        
        out = self.output_dir / output_name
        scene.save(str(out))
        return str(out)
    
    def _parse_position(self, pos_str, canvas_size, obj_size):
        """解析位置字符串 → 像素坐标"""
        if pos_str == "center":
            return (canvas_size - obj_size) // 2
        if pos_str.startswith("right"):
            base = canvas_size - obj_size
            offset = int(pos_str.replace("right", "")) if pos_str != "right" else 0
            return base + offset
        if pos_str.startswith("bottom"):
            base = canvas_size - obj_size
            offset = int(pos_str.replace("bottom", "")) if pos_str != "bottom" else 0
            return base + offset
        return int(pos_str)


# 分镜合成配方
class StoryboardRecipe:
    """分镜合成配置"""
    
    @staticmethod
    def EP01_FJ01():
        return {
            "scene": "场景01_林浩小屋",
            "characters": [
                {"name": "林浩", "scale": 0.25, "x": "right-60", "y": "bottom+10", "brightness": 0.7}
            ],
            "output": "EP01_分镜01_林浩写作.png"
        }
    
    @staticmethod
    def EP01_FJ03():
        return {
            "scene": "场景01_林浩小屋",
            "characters": [
                {"name": "林浩", "scale": 0.3, "x": "center", "y": "bottom", "brightness": 0.6}
            ],
            "output": "EP01_分镜03_凝视屏幕.png"
        }

compositor = ComicCompositor()
