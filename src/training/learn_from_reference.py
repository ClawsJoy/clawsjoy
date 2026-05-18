"""从参考漫剧学习风格"""
import json
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')

from lib.memory_simple import memory

def learn_from_zhetian():
    """学习《遮天》短剧的制作经验"""
    
    # 加载分析数据
    with open('data/training/zhetian_style.json') as f:
        style = json.load(f)
    
    # 存储到记忆系统
    memory.remember(
        json.dumps({
            "type": "reference_style",
            "name": "zhetian",
            "data": style
        }),
        category="reference_styles"
    )
    
    # 存储成功经验
    memory.remember(
        json.dumps({
            "type": "production_lesson",
            "source": "zhetian",
            "lesson": "AI可用于场景还原，但需人工把关角色设定",
            "applicable": ["script_generation", "character_design", "scene_render"]
        }),
        category="production_lessons"
    )
    
    print("🧠 大脑已学习《遮天》风格")
    print(f"📚 参考风格: {style['style_name']}")
    print(f"🎭 角色设定: {list(style['character_design'].keys())}")
    print(f"🏞️ 场景: {list(style['scene_description'].keys())}")

if __name__ == "__main__":
    learn_from_zhetian()
