#!/usr/bin/env python3
"""Rss Topic Crawler - Rss Topic Crawler 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import feedparser
from collections import Counter
from datetime import datetime
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from src.lib.vector.vector_manager import vector_manager

class RSSTopicCrawlerSkill:
    name = "rss_topic_crawler"
    description = "从 RSS 订阅源采集热点话题"
    version = "1.0.0"
    category = "crawler"
    
    # 停用词（不采集）
    STOP_WORDS = {
        'the', 'and', 'for', 'you', 'your', 'with', 'that', 'this', 'have', 
        'from', 'they', 'will', 'are', 'was', 'were', 'been', 'can', 'all',
        'tools', 'content', 'time', 'free', 'traffic', 'affiliate', 'marketing',
        'sovereign', 'creation', 'studio', 'transform', 'glasses', 'meta'
    }
    
    # 有价值的关键词（优先采集）
    VALUABLE_WORDS = {
        'chatgpt', 'openai', 'claude', 'gemini', 'llama', 'gpt', 'ai', 'ml',
        'python', 'javascript', 'rust', 'typescript', 'react', 'vue', 'angular',
        'docker', 'kubernetes', 'aws', 'azure', 'cloud', 'security', 'privacy',
        'database', 'api', 'microservice', 'devops', 'github', 'git', 'vscode'
    }
    
    # 免费 RSS 源
    RSS_FEEDS = {
        "tech": [
            "https://feeds.feedburner.com/TechCrunch",
            "https://www.theverge.com/rss/index.xml",
            "https://hnrss.org/frontpage"
        ]
    }
    
    def execute(self, params):
        sources = params.get("sources", ["tech"])
        limit = params.get("limit", 30)
        
        all_keywords = []
        
        for source in sources:
            for feed_url in self.RSS_FEEDS.get(source, []):
                try:
                    print(f"  📡 读取: {feed_url}")
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:15]:
                        title = entry.get('title', '')
                        # 转换为小写
                        words = title.lower().split()
                        # 过滤：长度>3，不是停用词
                        keywords = [w for w in words if len(w) > 3 and w not in self.STOP_WORDS]
                        all_keywords.extend(keywords)
                except Exception as e:
                    print(f"  ❌ 失败: {feed_url} - {e}")
        
        # 统计词频
        word_count = Counter(all_keywords)
        
        # 优先采集有价值的关键词
        valuable_found = {k: v for k, v in word_count.items() if k in self.VALUABLE_WORDS}
        other_found = {k: v for k, v in word_count.items() if k not in self.VALUABLE_WORDS and v >= 2}
        
        # 合并
        all_filtered = {**valuable_found, **other_found}
        sorted_keywords = sorted(all_filtered.items(), key=lambda x: x[1], reverse=True)
        top_keywords = sorted_keywords[:limit]
        
        # 存入向量库
        stored = []
        for keyword, count in top_keywords:
            vector_manager.add_knowledge(
                f"热点关键词: {keyword} (出现{count}次)",
                category="hot_topic",
                metadata={"keyword": keyword, "frequency": count, "source": "rss"}
            )
            stored.append(keyword)
        
        return {
            "success": True,
            "keywords_found": len(all_keywords),
            "stored": len(stored),
            "valuable_found": len(valuable_found),
            "top_keywords": top_keywords[:15],
            "message": f"已采集 {len(stored)} 个热点关键词"
        }

skill = RSSTopicCrawlerSkill()
