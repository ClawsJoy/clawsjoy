#!/usr/bin/env python3
"""Learn Anime Style - Learn Anime Style 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import json
import sys

from lib.smart_config import smart_config

sys.path.insert(0, "str(smart_config.ROOT)")

from lib.memory_simple import memory


def learn_anime_style():
    """学习腾讯动画版《遮天》的制作风格"""

    # 加载风格数据
    with open("data/training/zhetian_anime_style.json") as f:
        style = json.load(f)

    # 存储到记忆
    memory.remember(
        json.dumps({"type": "anime_style", "name": "zhetian_tengxun", "data": style}),
        category="animation_styles",
    )

    # 存储角色模板
    for role_name, role_data in style.get("character_templates", {}).items():
        memory.remember(
            json.dumps(
                {"type": "character_template", "role": role_name, "data": role_data}
            ),
            category="character_templates",
        )

    # 存储场景模板
    for scene_name, scene_data in style.get("scene_templates", {}).items():
        memory.remember(
            json.dumps(
                {"type": "scene_template", "scene": scene_name, "data": scene_data}
            ),
            category="scene_templates",
        )

    print(f"🧠 已学习动画版《遮天》风格")
    print(f"   - 角色模板: {list(style['character_templates'].keys())}")
    print(f"   - 场景模板: {list(style['scene_templates'].keys())}")


if __name__ == "__main__":
    learn_anime_style()
