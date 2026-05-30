#!/usr/bin/env python3
"""Smart Crawler - Smart Crawler 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from src.skills.atomic.crawler.web_crawler import skill as web_crawler

class SmartCrawlerSkill:
    name = "smart_crawler"
    description = "智能爬虫：种子URL自动发现和扩展"
    version = "1.0.0"
    category = "crawler"
    
    def execute(self, params):
        seed_url = params.get("seed_url", "")
        max_pages = params.get("max_pages", 5)
        
        if not seed_url:
            return {"success": False, "error": "需要提供种子URL"}
        
        print(f"🌱 种子URL: {seed_url}")
        
        visited = set()
        to_visit = [seed_url]
        results = []
        
        while to_visit and len(results) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)
            
            # 抓取当前页面
            result = web_crawler.execute({"url": url})
            if result.get("success"):
                results.append({"url": url, "status": "success"})
                print(f"  ✅ 已抓取: {url[:60]}...")
            
            # 简单延迟
            import time
            time.sleep(1)
        
        return {
            "success": True,
            "seed_url": seed_url,
            "crawled": len(results),
            "results": results,
            "message": f"已抓取 {len(results)} 个页面"
        }

skill = SmartCrawlerSkill()
