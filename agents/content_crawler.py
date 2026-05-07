#!/usr/bin/env python3
"""内容采集特工 - 专门抓取和提取内容"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import hashlib

class ContentCrawler:
    def __init__(self):
        self.content_dir = Path("data/content/raw")
        self.content_dir.mkdir(parents=True, exist_ok=True)
    
    def crawl(self, url, category="通用"):
        """采集单个 URL 的内容"""
        try:
            resp = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 提取正文
            for tag in soup(['script', 'style', 'nav', 'footer']):
                tag.decompose()
            
            text = soup.get_text()
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            content = '\n'.join(lines[:200])  # 前200行
            
            # 保存
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            filename = self.content_dir / f"{url_hash}_{category}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"来源: {url}\n分类: {category}\n\n{content}")
            
            return {"success": True, "file": str(filename), "length": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def batch_crawl(self, urls, category):
        """批量采集"""
        results = []
        for url in urls:
            result = self.crawl(url, category)
            results.append(result)
        return results

if __name__ == "__main__":
    crawler = ContentCrawler()
    result = crawler.crawl("https://www.immd.gov.hk/hks/services/index.html", "移民")
    print(result)
