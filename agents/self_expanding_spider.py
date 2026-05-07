#!/usr/bin/env python3
"""自扩展采集器 - 自动发现和采集新内容"""

import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import time

class SelfExpandingSpider:
    def __init__(self):
        self.seeds_file = Path("config/seed_urls.json")
        self.urls_db = Path("data/urls/discovered.json")
        self.content_dir = Path("data/content")
        self.content_dir.mkdir(parents=True, exist_ok=True)
        self.load_data()
    
    def load_data(self):
        # 加载种子
        with open(self.seeds_file) as f:
            self.seeds = json.load(f)
        
        # 加载已发现的 URL
        if self.urls_db.exists():
            with open(self.urls_db) as f:
                self.discovered = json.load(f)
        else:
            self.discovered = {}
    
    def save_discovered(self):
        with open(self.urls_db, 'w') as f:
            json.dump(self.discovered, f, ensure_ascii=False, indent=2)
    
    def extract_links(self, url, domain):
        """提取页面内的相关链接"""
        try:
            resp = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(url, href)
                if domain in full_url:
                    links.append(full_url)
            return list(set(links))
        except:
            return []
    
    def crawl_and_discover(self, url, category):
        """采集内容并发现新链接"""
        domain = urlparse(url).netloc
        
        # 采集内容
        try:
            resp = requests.get(url, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            text = soup.get_text()
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            content = '\n'.join(lines[:100])
            
            # 保存内容
            filename = url.replace('/', '_').replace(':', '_')[:100] + '.txt'
            with open(self.content_dir / filename, 'w', encoding='utf-8') as f:
                f.write(f"来源: {url}\n分类: {category}\n\n{content}")
            
            print(f"✅ 已采集: {url[:80]}...")
            
            # 发现新链接
            new_links = self.extract_links(url, domain)
            for link in new_links[:10]:  # 每页最多10个
                if link not in self.discovered:
                    self.discovered[link] = {"category": category, "source": url, "status": "pending"}
            
            self.save_discovered()
            return True
        except Exception as e:
            print(f"❌ 采集失败: {url}, {e}")
            return False
    
    def run(self):
        """运行自扩展采集"""
        # 1. 先采集种子 URL
        print("📡 第一阶段：采集种子 URL")
        for city, urls in self.seeds.items():
            for item in urls:
                print(f"\n🌆 {city} - {item['category']}")
                self.crawl_and_discover(item['url'], item['category'])
                time.sleep(2)
        
        # 2. 采集新发现的 URL
        print("\n📡 第二阶段：采集新发现的 URL")
        pending = [url for url, info in self.discovered.items() if info.get('status') == 'pending']
        for url in pending[:20]:  # 每次最多20个
            category = self.discovered[url].get('category', '通用')
            self.crawl_and_discover(url, category)
            self.discovered[url]['status'] = 'done'
            self.save_discovered()
            time.sleep(1)
        
        print(f"\n✅ 完成！共采集 {len(self.discovered)} 个 URL")

if __name__ == "__main__":
    spider = SelfExpandingSpider()
    spider.run()

from keyword_manager import KeywordManager

class EnhancedSpider(SelfExpandingSpider):
    def __init__(self):
        super().__init__()
        self.keyword_mgr = KeywordManager()
    
    def search_by_keyword(self, keyword):
        """根据关键词搜索相关内容"""
        category = self.keyword_mgr.suggest_for_input(keyword)
        print(f"🎯 关键词 '{keyword}' → 分类 '{category}'")
        
        # 获取该分类的种子 URL
        for city, urls in self.seeds.items():
            for item in urls:
                if item['category'] == category:
                    self.crawl_and_discover(item['url'], category)
    
    def learn_from_result(self, text, successful):
        """从采集结果学习新词"""
        if successful:
            self.keyword_mgr.learn_from_query(text)
