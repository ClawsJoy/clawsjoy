#!/usr/bin/env python3
"""新闻抓取服务 - 带去重功能"""

import sys
import os
import json
import time
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.news_engine import news_engine
from core.lib.vector_knowledge_center import vector_knowledge_center

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("news_crawler")

DATA_DIR = Path("data/news_cache")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 记录已抓取的新闻标题（用于去重）
SEEN_FILE = DATA_DIR / "seen_titles.json"


class NewsCrawler:
    def __init__(self):
        self.sources = {
            "toutiao_hot": {"name": "头条热搜", "method": "get_toutiao_hot"},
            "network_hot": {"name": "全网热搜", "method": "get_network_hot"},
            "it": {"name": "IT资讯", "method": "get_it"},
            "ai": {"name": "AI资讯", "method": "get_ai"},
            "keji": {"name": "科技资讯", "method": "get_keji"},
        }
        self.seen_titles = self._load_seen_titles()
    
    def _load_seen_titles(self):
        """加载已见标题"""
        if SEEN_FILE.exists():
            with open(SEEN_FILE, 'r') as f:
                data = json.load(f)
                # 只保留最近7天的记录
                cutoff = datetime.now() - timedelta(days=7)
                return {k: v for k, v in data.items() if datetime.fromisoformat(v) > cutoff}
        return {}
    
    def _save_seen_titles(self):
        """保存已见标题"""
        with open(SEEN_FILE, 'w') as f:
            json.dump(self.seen_titles, f, indent=2)
    
    def _is_duplicate(self, title: str) -> bool:
        """检查是否重复"""
        return title in self.seen_titles
    
    def _mark_seen(self, title: str):
        """标记为已见"""
        self.seen_titles[title] = datetime.now().isoformat()
    
    def _build_content(self, category: str, item: dict) -> str:
        """构建文档内容"""
        title = item.get('title', item.get('word', ''))
        lines = [f"【{category}】{title}"]
        
        if 'hotindex' in item:
            lines.append(f"热度: {item['hotindex']}")
        if 'hotnum' in item:
            lines.append(f"热度: {item['hotnum']}")
        if 'source' in item:
            lines.append(f"来源: {item['source']}")
        if 'url' in item:
            lines.append(f"链接: {item['url']}")
        if 'ctime' in item:
            lines.append(f"时间: {item['ctime']}")
        
        return "\n".join(lines)
    
    def _save_to_vector(self, category: str, items: list) -> int:
        """保存到向量库（带去重）"""
        if not items:
            return 0
        
        count = 0
        skipped = 0
        
        for item in items:
            title = item.get('title', item.get('word', ''))
            
            # 去重检查
            if self._is_duplicate(title):
                skipped += 1
                continue
            
            content = self._build_content(category, item)
            # 使用标题+来源生成唯一 ID
            unique_key = f"{category}_{title}"
            doc_id = hashlib.md5(unique_key.encode()).hexdigest()
            
            try:
                vector_knowledge_center.add_document(
                    doc_id=doc_id,
                    content=content,
                    metadata={
                        "category": category,
                        "title": title,
                        "source": item.get('source', ''),
                        "url": item.get('url', '')
                    }
                )
                self._mark_seen(title)
                count += 1
            except Exception as e:
                logger.error(f"添加失败: {e}")
        
        self._save_seen_titles()
        return count, skipped
    
    def crawl_category(self, category: str, limit: int = 15) -> tuple:
        source = self.sources.get(category)
        if not source:
            return 0, 0
        method = getattr(news_engine, source["method"], None)
        if not method:
            return 0, 0
        try:
            items = method(limit)
            if items:
                count, skipped = self._save_to_vector(category, items)
                # 本地备份
                backup = DATA_DIR / f"{category}_{datetime.now().strftime('%Y%m%d')}.json"
                with open(backup, 'w') as f:
                    json.dump(items, f, indent=2, ensure_ascii=False)
                logger.info(f"✅ {source['name']}: 抓取 {len(items)} 条，新增 {count} 条，跳过 {skipped} 条重复")
                return count, skipped
        except Exception as e:
            logger.error(f"❌ {category}: {e}")
        return 0, 0
    
    def crawl_all(self, limit: int = 15) -> dict:
        results = {}
        total_new = 0
        total_skipped = 0
        for category in self.sources:
            new_count, skipped = self.crawl_category(category, limit)
            results[category] = {"new": new_count, "skipped": skipped}
            total_new += new_count
            total_skipped += skipped
            time.sleep(1)
        
        logger.info(f"📊 本次抓取: 新增 {total_new} 条，跳过重复 {total_skipped} 条")
        return results


if __name__ == "__main__":
    crawler = NewsCrawler()
    print("开始抓取新闻（带去重）...")
    results = crawler.crawl_all(15)
    print(f"抓取完成: {results}")
