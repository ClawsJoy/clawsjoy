#!/usr/bin/env python3
"""URL 采集技能 - 根据 URL 或关键词采集内容"""

import json
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import sys

# 采集源配置（可动态添加）
SOURCES = {
    "香港入境处": {
        "url": "https://www.immd.gov.hk/hks/services/index.html",
        "type": "政府",
        "category": ["移民", "签证", "身份"]
    },
    "香港政府新闻": {
        "url": "https://www.info.gov.hk/gia/general/today.htm",
        "type": "新闻",
        "category": ["新闻", "政策", "时事"]
    },
    "香港教育局": {
        "url": "https://www.edb.gov.hk/sc/",
        "type": "政府",
        "category": ["教育", "留学", "学校"]
    },
    "香港劳工处": {
        "url": "https://www.labour.gov.hk/tc/",
        "type": "政府",
        "category": ["工作", "就业", "招聘"]
    },
    "香港医管局": {
        "url": "https://www.ha.org.hk/",
        "type": "政府",
        "category": ["医疗", "健康", "医院"]
    },
    "香港旅游发展局": {
        "url": "https://www.discoverhongkong.com/sc/index.html",
        "type": "旅游",
        "category": ["旅游", "美食", "景点"]
    }
}

def add_source(name, url, category, source_type="用户添加"):
    """动态添加采集源"""
    SOURCES[name] = {
        "url": url,
        "type": source_type,
        "category": [category] if isinstance(category, str) else category
    }
    return {"success": True, "name": name, "url": url}

def get_sources_by_category(category):
    """根据分类获取采集源"""
    results = []
    for name, info in SOURCES.items():
        if category in info.get('category', []):
            results.append({"name": name, "url": info['url']})
    return results

def crawl_url(url, max_length=3000):
    """采集指定 URL 的内容"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 移除脚本和样式
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        text = soup.get_text()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        content = '\n'.join(lines)
        
        return content[:max_length]
    except Exception as e:
        return f"采集失败: {e}"

def execute(params):
    """执行采集任务"""
    action = params.get('action', 'crawl')
    
    if action == 'crawl':
        url = params.get('url')
        if not url:
            return {"error": "需要提供 url 参数"}
        content = crawl_url(url)
        return {"success": True, "content": content, "url": url}
    
    elif action == 'search':
        category = params.get('category')
        if not category:
            return {"error": "需要提供 category 参数"}
        sources = get_sources_by_category(category)
        return {"success": True, "sources": sources}
    
    elif action == 'add':
        name = params.get('name')
        url = params.get('url')
        category = params.get('category')
        if not all([name, url, category]):
            return {"error": "需要 name, url, category 参数"}
        result = add_source(name, url, category)
        return result
    
    return {"error": f"未知 action: {action}"}

if __name__ == "__main__":
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = execute(params)
    print(json.dumps(result, ensure_ascii=False, indent=2))
