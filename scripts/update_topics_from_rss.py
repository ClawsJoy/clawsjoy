from lib.smart_config import smart_config
#!/usr/bin/env python3
"""从 RSS 订阅源自动提取话题关键词"""
import feedparser
import jieba
import json
from collections import Counter
from pathlib import Path

# RSS 源列表
RSS_FEEDS = [
    "https://www.ruanyifeng.com/blog/atom.xml",
    "https://feed.cnblogs.com/",
]

def extract_topics_from_rss():
    """从 RSS 提取热门关键词"""
    all_words = []
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]:
                title = entry.get('title', '')
                # 中文分词提取关键词
                words = jieba.lcut(title)
                words = [w for w in words if len(w) >= 2]
                all_words.extend(words)
        except Exception as e:
            print(f"  RSS 失败 {url}: {e}")
    
    # 统计词频
    word_count = Counter(all_words)
    # 过滤常见停用词
    stopwords = {'今日', '热门', '推荐', '原创', '转载', '首页'}
    topics = [(w, c) for w, c in word_count.most_common(30) if w not in stopwords]
    
    return topics

if __name__ == "__main__":
    topics = extract_topics_from_rss()
    print("提取到的话题:")
    for topic, count in topics[:10]:
        print(f"  {topic}: {count}次")
