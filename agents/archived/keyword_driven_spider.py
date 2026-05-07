#!/usr/bin/env python3
"""关键词驱动采集 - 根据关键词自动选择采集源和策略"""

import re
import requests
from bs4 import BeautifulSoup

# 关键词 → 采集源映射
KEYWORD_SOURCES = {
    # 香港
    r'优才|高才|人才引进|香港身份': {
        'url': 'https://www.immd.gov.hk/hks/services/index.html',
        'site': '香港入境处',
        'city': '香港'
    },
    r'香港新闻|香港动态|香港政策': {
        'url': 'https://www.info.gov.hk/gia/general/today.htm',
        'site': '香港政府新闻',
        'city': '香港'
    },
    r'香港留学|香港大学|香港教育': {
        'url': 'https://www.edb.gov.hk/sc/',
        'site': '香港教育局',
        'city': '香港'
    },
    # 上海
    r'上海人才|上海落户|上海政策': {
        'url': 'https://www.shanghai.gov.cn/',
        'site': '上海市政府',
        'city': '上海'
    },
    # 深圳
    r'深圳人才|深圳落户|深圳政策': {
        'url': 'https://hrss.sz.gov.cn/',
        'site': '深圳人社局',
        'city': '深圳'
    }
}

def extract_keywords(text):
    """从用户输入中提取关键词"""
    keywords = []
    for pattern in KEYWORD_SOURCES.keys():
        if re.search(pattern, text):
            keywords.append(pattern)
    return keywords

def get_source_by_keyword(keyword):
    """根据关键词获取采集源"""
    for pattern, source in KEYWORD_SOURCES.items():
        if re.search(pattern, keyword):
            return source
    return None

def crawl(source):
    """执行采集"""
    try:
        resp = requests.get(source['url'], timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text()
        # 提取前500字
        return text[:2000]
    except Exception as e:
        return f"采集失败: {e}"

def execute(user_input):
    """关键词驱动的主流程"""
    print(f"📝 用户输入: {user_input}")
    
    # 1. 提取关键词
    keywords = extract_keywords(user_input)
    if not keywords:
        return {"error": "未识别到关键词", "suggest": "试试：香港优才、上海人才、深圳政策"}
    
    print(f"🔑 识别关键词: {keywords}")
    
    # 2. 根据第一个关键词确定采集源
    source = get_source_by_keyword(keywords[0])
    if not source:
        return {"error": "无对应采集源"}
    
    print(f"📍 采集源: {source['site']} ({source['city']})")
    
    # 3. 执行采集
    content = crawl(source)
    
    return {
        "city": source['city'],
        "source": source['site'],
        "content": content[:1000],
        "keywords": keywords
    }

if __name__ == "__main__":
    import sys
    tests = [
        "香港优才计划最新政策",
        "上海人才引进有什么新政策",
        "深圳落户条件",
        "香港大学申请指南"
    ]
    
    for test in tests:
        result = execute(test)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("-" * 50)
