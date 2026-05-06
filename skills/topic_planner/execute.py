#!/usr/bin/env python3
"""话题规划"""
import sys, json, random
from datetime import datetime

TOPICS = {
    "immigration": [
        "香港优才计划2026最新政策解读",
        "香港高才通申请全攻略",
        "香港专才计划 vs 优才计划区别",
        "香港投资移民重启细节"
    ],
    "education": [
        "香港大学2026本科申请指南",
        "香港科技大学热门专业推荐",
        "香港中文大学研究生申请条件",
        "香港留学一年费用明细"
    ],
    "life": [
        "香港生活成本大揭秘",
        "香港租房攻略：哪里性价比高",
        "香港美食探店：必吃清单",
        "香港交通攻略：八达通vs月票"
    ],
    "news": [
        "香港北部都会区最新进展",
        "香港人才引进政策变化",
        "香港通关最新消息"
    ]
}

def execute(params):
    category = params.get("category", random.choice(list(TOPICS.keys())))
    count = params.get("count", 1)
    
    topics = TOPICS.get(category, TOPICS["immigration"])
    selected = topics[:count]
    
    return {
        "success": True,
        "topics": selected,
        "category": category,
        "date": datetime.now().strftime("%Y-%m-%d")
    }

if __name__ == "__main__":
    params = json.loads(sys.argv[1])
    print(json.dumps(execute(params)))
