#!/usr/bin/env python3
"""通用意图解析 - 自动提取主题、地点、风格"""

import json
import re
import requests

def parse_intent(user_input):
    """解析用户输入，提取关键信息"""
    
    # 地点识别
    cities = {
        '香港': ['香港', 'hongkong', 'hk'],
        '上海': ['上海', 'shanghai'],
        '深圳': ['深圳', 'shenzhen'],
        '北京': ['北京', 'beijing'],
        '广州': ['广州', 'guangzhou']
    }
    
    # 主题识别
    topics = {
        '人才政策': ['人才', '政策', '引进', '优才', '高才', '落户'],
        '留学': ['留学', '大学', '申请', '读研'],
        '生活': ['生活', '租房', '美食', '旅游'],
        '工作': ['工作', '就业', '招聘', '工资']
    }
    
    # 风格识别
    styles = {
        '专业': ['政策', '解读', '分析', '攻略'],
        '轻松': ['分享', 'vlog', '日常', '探店'],
        '新闻': ['最新', '消息', '动态', '通知']
    }
    
    text = user_input.lower()
    
    # 提取地点
    location = '香港'  # 默认
    for city, keywords in cities.items():
        if any(kw in text for kw in keywords):
            location = city
            break
    
    # 提取主题
    topic = '人才政策'  # 默认
    for tp, keywords in topics.items():
        if any(kw in text for kw in keywords):
            topic = tp
            break
    
    # 提取风格
    style = '专业'  # 默认
    for st, keywords in styles.items():
        if any(kw in text for kw in keywords):
            style = st
            break
    
    return {
        'location': location,
        'topic': topic,
        'style': style,
        'raw': user_input
    }

if __name__ == "__main__":
    tests = [
        "做一个上海人才引进的视频",
        "深圳留学申请攻略",
        "香港生活成本大揭秘",
        "北京最新政策解读"
    ]
    
    for t in tests:
        result = parse_intent(t)
        print(f"{t} → {result}")
