#!/usr/bin/env python3
"""URL 采集特工 - 专门发现和验证 URL"""

import json
import requests
from urllib.parse import urlparse
from pathlib import Path

class URLScout:
    def __init__(self):
        self.url_db = Path("data/urls/discovered.json")
        self.load()
    
    def load(self):
        if self.url_db.exists():
            with open(self.url_db) as f:
                self.urls = json.load(f)
        else:
            self.urls = {}
    
    def save(self):
        with open(self.url_db, 'w') as f:
            json.dump(self.urls, f, ensure_ascii=False, indent=2)
    
    def discover_from_seed(self, seed_url, depth=1):
        """从种子 URL 发现新链接"""
        print(f"🔍 探索种子: {seed_url}")
        domain = urlparse(seed_url).netloc
        
        try:
            resp = requests.get(seed_url, timeout=10)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            new_urls = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('http') and domain in href:
                    if href not in self.urls:
                        self.urls[href] = {
                            "source": seed_url,
                            "status": "pending",
                            "discovered_at": str(__import__('time').time())
                        }
                        new_urls.append(href)
            
            self.save()
            print(f"✅ 发现 {len(new_urls)} 个新 URL")
            return new_urls
        except Exception as e:
            print(f"❌ 探索失败: {e}")
            return []
    
    def validate(self, url):
        """验证 URL 是否可访问"""
        try:
            resp = requests.head(url, timeout=5, allow_redirects=True)
            return resp.status_code < 400
        except:
            return False
    
    def get_next_pending(self, limit=10):
        """获取待采集的 URL"""
        pending = [url for url, info in self.urls.items() if info.get('status') == 'pending']
        return pending[:limit]

if __name__ == "__main__":
    scout = URLScout()
    scout.discover_from_seed("https://www.immd.gov.hk/hks/")
    print(f"待采集: {len(scout.get_next_pending())}")
