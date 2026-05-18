"""真实热点爬虫 - 可爬取的免费源"""
import requests
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from src.lib.vector.vector_manager import vector_manager

class RealHotCrawlerSkill:
    name = "real_hot_crawler"
    description = "从可爬取的免费源获取热点"
    version = "1.0.0"
    category = "crawler"
    
    # 可爬取的热点源
    SOURCES = {
        "zhihu": {
            "name": "知乎热榜",
            "url": "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=20",
            "type": "api",
            "parser": "json"
        },
        "baidu": {
            "name": "百度热搜",
            "url": "https://top.baidu.com/board?tab=realtime",
            "type": "html",
            "parser": "html"
        },
        "weibo": {
            "name": "微博热搜",
            "url": "https://weibo.com/ajax/side/hotSearch",
            "type": "api",
            "parser": "json"
        },
        "toutiao": {
            "name": "今日头条",
            "url": "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc",
            "type": "api",
            "parser": "json"
        }
    }
    
    def execute(self, params):
        platforms = params.get("platforms", ["zhihu", "baidu", "weibo"])
        results = {}
        
        for platform in platforms:
            if platform in self.SOURCES:
                data = self._fetch(platform)
                results[platform] = data
                print(f"  ✅ {self.SOURCES[platform]['name']}: {len(data)} 条")
        
        # 统计合并
        all_topics = []
        for platform, topics in results.items():
            all_topics.extend(topics)
        
        # 词频统计
        word_count = {}
        for topic in all_topics:
            word_count[topic] = word_count.get(topic, 0) + 1
        
        # 存入向量库
        stored = []
        for topic, count in list(word_count.items())[:15]:
            vector_manager.add_knowledge(
                f"热点: {topic} (来源数:{count})",
                category="hot_topic",
                metadata={"topic": topic, "frequency": count, "collected_at": datetime.now().isoformat()}
            )
            stored.append({"topic": topic, "count": count})
        
        return {
            "success": True,
            "platforms": list(results.keys()),
            "total_topics": len(all_topics),
            "stored": len(stored),
            "message": f"已采集 {len(stored)} 条热点"
        }
    
    def _fetch(self, platform):
        """获取各平台热点"""
        source = self.SOURCES[platform]
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            resp = requests.get(source["url"], headers=headers, timeout=10)
            
            if source["parser"] == "json":
                return self._parse_json(resp.json(), platform)
            else:
                return self._parse_html(resp.text, platform)
        except Exception as e:
            print(f"  ❌ {source['name']} 失败: {e}")
            return []
    
    def _parse_json(self, data, platform):
        """解析JSON响应"""
        topics = []
        if platform == "zhihu":
            for item in data.get("data", []):
                topic = item.get("target", {}).get("title", "")
                if topic:
                    topics.append(topic)
        elif platform == "weibo":
            for item in data.get("data", {}).get("realtime", []):
                topic = item.get("word", "")
                if topic:
                    topics.append(topic)
        return topics[:15]
    
    def _parse_html(self, html, platform):
        """解析HTML响应"""
        topics = []
        if platform == "baidu":
            soup = BeautifulSoup(html, 'html.parser')
            for item in soup.select('.topic-content'):
                text = item.get_text().strip()
                if text and len(text) < 30:
                    topics.append(text)
        return topics[:15]

skill = RealHotCrawlerSkill()
