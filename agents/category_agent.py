#!/usr/bin/env python3
"""分类驱动 Agent - 根据用户输入自动归类并采集"""

import json
import re

# 加载分类配置
with open('config/hk_categories.json', 'r') as f:
    CATEGORIES = json.load(f)

def detect_category(text):
    """检测用户输入属于哪个大类"""
    text_lower = text.lower()
    
    for cat, info in CATEGORIES.items():
        for kw in info['keywords']:
            if kw in text_lower:
                return cat, info
    return None, None

def detect_subcategory(text, category_info):
    """检测具体子类"""
    text_lower = text.lower()
    for sub in category_info.get('sub', []):
        if sub in text_lower:
            return sub
    return category_info['sub'][0] if category_info['sub'] else None

def execute(user_input):
    print(f"📝 用户: {user_input}")
    
    # 1. 分类
    category, info = detect_category(user_input)
    if not category:
        return {"error": "无法识别分类", "suggest": "试试：移民、留学、生活、工作、医疗"}
    
    print(f"📁 分类: {category} - {info.get('sub')}")
    
    # 2. 子类
    sub = detect_subcategory(user_input, info)
    if sub:
        print(f"📌 子类: {sub}")
    
    # 3. 确定风格
    style = info.get('风格', '专业')
    print(f"🎨 风格: {style}")
    
    # 4. 确定采集源
    source = info.get('采集源', '通用')
    print(f"📡 采集源: {source}")
    
    return {
        "category": category,
        "subcategory": sub,
        "style": style,
        "source": source,
        "original": user_input
    }

if __name__ == "__main__":
    tests = [
        "香港优才计划怎么申请",
        "香港留学一年多少钱",
        "香港找工作难吗",
        "香港租房哪里便宜",
        "香港美食推荐",
        "香港看病贵不贵"
    ]
    
    for test in tests:
        result = execute(test)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("-" * 50)
