#!/usr/bin/env python3
"""关键词驱动工作流 - 根据用户输入自动匹配工作流"""

import json
import sys
import re
from pathlib import Path

# 加载关键词库
def load_keywords():
    try:
        with open('/mnt/d/clawsjoy/data/keywords.json', 'r') as f:
            return json.load(f)
    except:
        return {"keywords": []}

# 加载分类关键词
def load_categories():
    try:
        with open('/mnt/d/clawsjoy/config/hk_categories.json', 'r') as f:
            return json.load(f)
    except:
        return {}

# 匹配工作流
def match_workflow(user_input, keywords_data, categories):
    user_input_lower = user_input.lower()
    
    # 按分类匹配
    for category, info in categories.items():
        for kw in info.get("keywords", []):
            if kw in user_input_lower:
                return {
                    "workflow": "hk_production",
                    "category": category,
                    "style": info.get("风格", "专业"),
                    "keyword": kw
                }
    
    # 默认工作流
    return {
        "workflow": "test_flow",
        "category": "通用",
        "style": "科技",
        "keyword": "香港"
    }

if __name__ == "__main__":
    user_input = sys.argv[1] if len(sys.argv) > 1 else "制作香港宣传片"
    keywords = load_keywords()
    categories = load_categories()
    result = match_workflow(user_input, keywords, categories)
    print(json.dumps(result, ensure_ascii=False, indent=2))
