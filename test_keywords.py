#!/usr/bin/env python3
"""测试 Unsplash 搜索词"""

import json
import random

# 搜索词配置
REAL_TERMS = {
    "base_terms": [
        "real street photography",
        "documentary style", 
        "on location shooting",
        "actual scene capture",
        "real life photography",
        "candid documentary",
        "street view real"
    ],
    "category_terms": {
        "immigration": ["government building", "official", "policy"],
        "education": ["university", "campus life", "students", "library"],
        "living": ["daily life", "street view", "local market"],
        "tech": ["modern office", "innovation", "tech park"],
        "culture": ["heritage", "traditional", "cultural"],
        "scenery": ["cityscape", "harbour view", "skyline"]
    }
}

def get_keyword(city, topic):
    topic_lower = topic.lower()
    
    # 判断类别
    if any(k in topic_lower for k in ["优才", "人才", "移民", "签证"]):
        cat = "immigration"
    elif any(k in topic_lower for k in ["留学", "大学", "教育"]):
        cat = "education"
    elif any(k in topic_lower for k in ["生活", "租房", "美食"]):
        cat = "living"
    elif any(k in topic_lower for k in ["科技", "创新", "AI"]):
        cat = "tech"
    elif any(k in topic_lower for k in ["文化", "历史", "传统"]):
        cat = "culture"
    else:
        cat = "scenery"
    
    base = random.choice(REAL_TERMS["base_terms"])
    cat_term = random.choice(REAL_TERMS["category_terms"].get(cat, ["cityscape"]))
    
    return f"{city} {cat_term} {base}"

# 测试
test_topics = [
    "香港优才计划2026最新政策",
    "香港大学申请指南", 
    "香港生活成本大揭秘",
    "香港科技发展前景",
    "香港历史文化景点",
    "香港维多利亚港风景"
]

print("=" * 50)
for topic in test_topics:
    keyword = get_keyword("香港", topic)
    print(f"{topic[:15]} → {keyword}")
print("=" * 50)
