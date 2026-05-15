"""热点信号采集 - 使用 RSS 订阅"""
import feedparser
from lib.hot_db import hot_db

class HotCollectorSkill:
    name = "hot_collector"
    description = "采集热点信号"
    version = "1.0.0"
    category = "analysis"

    def execute(self, params):
        # 使用 Google News RSS（无需代理）
        rss_urls = [
            "https://news.google.com/rss/search?q=香港+高才通&hl=zh-CN&ceid=CN:zh",
            "https://news.google.com/rss/search?q=香港+优才计划&hl=zh-CN&ceid=CN:zh"
        ]
        
        collected = 0
        for url in rss_urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:10]:
                    title = entry.get('title', '')
                    summary = entry.get('summary', '')
                    text = title + ' ' + summary
                    
                    keywords = {
                        "高才通": 10, "优才": 8, "续签": 8,
                        "人才计划": 6, "获批": 6
                    }
                    
                    for kw, weight in keywords.items():
                        if kw in text:
                            hot_db.add_signal(
                                keyword=kw,
                                source=entry.get('link', url),
                                热度=weight,
                                context=title[:200]
                            )
                            collected += 1
                            print(f"✅ 发现: {kw} - {title[:50]}")
            except Exception as e:
                print(f"RSS 采集失败: {e}")
        
        return {"success": True, "collected": collected}

skill = HotCollectorSkill()
