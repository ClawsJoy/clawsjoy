"""表情切换"""
from PIL import Image
from rembg import remove
from pathlib import Path
import os
class ExpressionSwitcher:
    def __init__(self):
        self.expressions = {}
        char_dir = Path('data/assets/novels/AI觉醒/characters/林浩/images')
        if char_dir.exists():
            for f in char_dir.glob("表情_*.png"):
                name = f.stem.replace("表情_", "")
                self.expressions[name] = str(f)
    def execute(self, params):
        text = params.get("text", "")
        mapping = {"复杂":"忧郁","思考":"沉思","谁":"惊讶","晚安":"温柔微笑","坚定":"坚定","窗外":"孤独凝视"}
        for kw, expr in mapping.items():
            if kw in text:
                return {"success": True, "expression": expr, "file": self.expressions.get(expr, "")}
        return {"success": True, "expression": "default"}
