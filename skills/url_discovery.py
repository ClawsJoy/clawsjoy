#!/usr/bin/env python3
"""URL 发现技能 - 从页面中提取链接并存储"""

import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys

# 存储文件
STORAGE_FILE = "data/discovered_urls.json"

def load_discovered():
    """加载已发现的链接"""
    import os
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_discovered(discovered):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(discovered, f, ensure_ascii=False, indent=2)

def extract_links(url, base_domain=None):
    """从页面提取链接"""
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(url, href)
            
            # 只保留同域名链接
            if base_domain:
                if base_domain in full_url:
                    links.append(full_url)
            else:
                if urlparse(full_url).netloc == urlparse(url).netloc:
                    links.append(full_url)
        
        return list(set(links))
    except Exception as e:
        print(f"提取失败: {e}")
        return []

def discover_and_store(seed_url, category="通用"):
    """发现链接并存储"""
    print(f"🔍 分析种子 URL: {seed_url}")
    
    # 提取链接
    domain = urlparse(seed_url).netloc
    links = extract_links(seed_url, domain)
    print(f"📎 发现 {len(links)} 个链接")
    
    # 加载已有数据
    discovered = load_discovered()
    
    # 存储新链接
    new_count = 0
    for link in links[:20]:  # 限制数量
        if link not in discovered:
            discovered[link] = {
                "source": seed_url,
                "category": category,
                "title": "",
                "discovered_at": str(__import__('time').time())
            }
            new_count += 1
    
    save_discovered(discovered)
    print(f"✅ 新增 {new_count} 个链接")
    
    return {"new_count": new_count, "total": len(discovered)}

if __name__ == "__main__":
    import sys
    seed = sys.argv[1] if len(sys.argv) > 1 else "https://www.immd.gov.hk/hks/"
    result = discover_and_store(seed, "移民")
    print(json.dumps(result, ensure_ascii=False))
