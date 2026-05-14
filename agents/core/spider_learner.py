#!/usr/bin/env python3
"""爬虫 Agent 专属学习 - URL 模式"""

import json
import re
from pathlib import Path
from base_learner import BaseLearner

class SpiderLearner(BaseLearner):
    def __init__(self):
        super().__init__("spider_agent", "crawling")
        self.url_file = Path("/mnt/d/clawsjoy/data/urls/discovered.json")
    
    def learn(self, new_knowledge=None):
        """学习 URL 模式"""
        if not self.url_file.exists():
            return []
        
        with open(self.url_file) as f:
            urls = json.load(f)
        
        # 分析域名模式
        domains = {}
        for url in urls.keys():
            match = re.search(r'https?://([^/]+)', url)
            if match:
                domain = match.group(1)
                domains[domain] = domains.get(domain, 0) + 1
        
        # 学习高频域名
        knowledge = []
        for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]:
            knowledge.append({
                "type": "domain_pattern",
                "domain": domain,
                "count": count,
                "learned_at": __import__('time').time()
            })
        
        self.learned["knowledge"] = knowledge
        self.learned["stats"]["total_domains"] = len(domains)
        self.save_learned()
        return knowledge
    
    def should_crawl(self, url):
        """判断是否应该爬取"""
        # 排除静态资源
        exclude = ['.jpg', '.png', '.gif', '.pdf', '.zip']
        if any(url.lower().endswith(ext) for ext in exclude):
            return False
        
        # 排除锚点
        if '#' in url:
            return False
        
        return True
    
    def get_seed_suggestions(self):
        """建议新的种子 URL"""
        knowledge = self.learned.get("knowledge", [])
        high_value_domains = [k["domain"] for k in knowledge if k.get("count", 0) > 5]
        return high_value_domains[:5]

if __name__ == "__main__":
    learner = SpiderLearner()
    learned = learner.learn()
    print(f"学习了 {len(learned)} 个域名模式")
    print(f"种子建议: {learner.get_seed_suggestions()}")
    print(f"统计: {learner.get_stats()}")
