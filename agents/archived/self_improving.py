#!/usr/bin/env python3
"""自完善系统 - 根据用户反馈动态扩展分类和采集源"""

import json
from pathlib import Path

CONFIG_FILE = Path("config/hk_categories.json")
FEEDBACK_FILE = Path("data/user_feedback.json")

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def record_feedback(user_input, category, satisfied):
    """记录用户反馈"""
    feedback = []
    if FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, 'r') as f:
            feedback = json.load(f)
    
    feedback.append({
        "input": user_input,
        "category": category,
        "satisfied": satisfied,
        "action": "add_to_config" if not satisfied else None
    })
    
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(feedback[-100:], f, ensure_ascii=False, indent=2)

def expand_category(user_input, category):
    """根据新需求扩展分类"""
    config = load_config()
    
    # 提取新关键词
    words = user_input.replace('香港', '').replace('怎么', '').replace('如何', '').strip()
    
    if category in config:
        # 添加新关键词到现有分类
        if words not in config[category]['keywords']:
            config[category]['keywords'].append(words)
            print(f"✅ 已添加关键词 '{words}' 到 {category}")
    else:
        # 创建新分类
        config[category] = {
            "sub": [words],
            "keywords": [words],
            "采集源": "待配置",
            "风格": "通用"
        }
        print(f"✅ 已创建新分类 '{category}'")
    
    save_config(config)

def learn_from_query(user_input, detected_category, user_satisfied):
    """从用户查询中学习"""
    if not user_satisfied:
        expand_category(user_input, detected_category or "新需求")
    
    record_feedback(user_input, detected_category, user_satisfied)

if __name__ == "__main__":
    # 示例：用户问了个新问题
    learn_from_query("香港宠物移民怎么办", "移民身份", False)
    learn_from_query("香港咖啡馆推荐", "生活消费", False)
    
    # 查看更新后的配置
    config = load_config()
    print(json.dumps(config, ensure_ascii=False, indent=2))
