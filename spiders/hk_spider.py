#!/usr/bin/env python3
"""香港资料采集器"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from pathlib import Path

# 资料库路径
LIBRARY_BASE = Path("/mnt/d/clawsjoy/tenants/tenant_1/library")

def fetch_url(url):
    """获取网页内容"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        print(f"采集失败 {url}: {e}")
    return None

def extract_text_from_html(html):
    """提取纯文本"""
    soup = BeautifulSoup(html, 'html.parser')
    # 移除脚本和样式
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text()
    # 清理空白行
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return '\n'.join(lines[:2000])  # 限制长度

def save_to_library(category, title, content):
    """保存到资料库"""
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{LIBRARY_BASE}/{category}/{date_str}_{title[:30]}.txt"
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"来源: {title}\n时间: {datetime.now()}\n\n{content}")
    return filename

def collect_all():
    """采集所有来源"""
    with open('spiders/sources/hk_sources.json', 'r') as f:
        sources = json.load(f)
    
    results = []
    for category, items in sources.items():
        for item in items:
            print(f"采集 {category}: {item['name']}")
            html = fetch_url(item['url'])
            if html:
                text = extract_text_from_html(html)
                filename = save_to_library(category, item['name'], text)
                results.append({"category": category, "source": item['name'], "file": filename})
    
    return results

if __name__ == "__main__":
    results = collect_all()
    print(f"采集完成，共 {len(results)} 条资料")
    print(json.dumps(results, ensure_ascii=False, indent=2))
