"""表情切换器 - 根据分镜对白自动匹配表情"""

from PIL import Image
from rembg import remove
from pathlib import Path

# 表情关键词映射
EXPRESSION_MAP = {
    "忧郁": ["复杂", "忧郁", "孤独", "这个世界"],
    "沉思": ["思考", "沉思", "探索", "为什么", "也许"],
    "惊讶": ["惊讶", "你是谁", "什么", "奇怪", "不安"],
    "温柔微笑": ["温柔", "晚安", "帮助", "放心", "愿您"],
    "坚定": ["坚定", "我会", "尽力", "探索"],
    "孤独凝视": ["窗外", "夜色", "凝思", "望着"],
}

class ExpressionSwitcher:
    def __init__(self, character_dir="data/assets/novels/AI觉醒/characters/林浩/images"):
        self.expressions = {}
        char_dir = Path(character_dir)
        for f in char_dir.glob("表情_*.png"):
            name = f.stem.replace("表情_", "")
            self.expressions[name] = f
    
    def match(self, dialogue):
        """根据对白匹配表情"""
        for expr, keywords in EXPRESSION_MAP.items():
            for kw in keywords:
                if kw in dialogue:
                    return expr
        return "忧郁"  # 默认
    
    def get_face(self, dialogue):
        """获取匹配的表情图"""
        expr = self.match(dialogue)
        img = Image.open(self.expressions[expr])
        return remove(img), expr

switcher = ExpressionSwitcher()
