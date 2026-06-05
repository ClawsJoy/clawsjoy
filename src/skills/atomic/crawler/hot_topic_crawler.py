#!/usr/bin/env python3
"""Hot Topic Crawler - Hot Topic Crawler 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import re
import sys
from datetime import datetime, timedelta

import requests

from lib.smart_config import smart_config

sys.path.insert(0, "str(smart_config.ROOT)")
from src.lib.vector.vector_manager import vector_manager


class HotTopicCrawlerSkill:
    name = "hot_topic_crawler"
    description = "采集热门话题（微博/百度/头条）"
    version = "1.0.0"
    category = "crawler"

    # 平台配置
    PLATFORMS = {
        "weibo": {
            "name": "微博热搜",
            "api": "https://weibo.com/ajax/side/hotSearch",
            "selector": "data",
        },
        "baidu": {
            "name": "百度热搜",
            "api": "https://top.baidu.com/board?tab=realtime",
            "selector": "html",
        },
        "toutiao": {
            "name": "今日头条",
            "api": "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc",
            "selector": "json",
        },
    }

    # 配置
    CONFIG = {
        "threshold": 5,  # 出现次数阈值
        "top_k": 5,  # 取前K条
        "retention_days": 30,  # 保留天数
    }

    def execute(self, params):
        platforms = params.get("platforms", ["weibo", "baidu", "toutiao"])

        print(f"🔥 采集热门话题: {platforms}")

        all_topics = []
        platform_results = {}

        for platform in platforms:
            if platform in self.PLATFORMS:
                topics = self._fetch_platform(platform)
                platform_results[platform] = topics
                all_topics.extend(topics)
                print(f"  📱 {self.PLATFORMS[platform]['name']}: {len(topics)} 条")

        # 统计词频
        word_count = {}
        for topic in all_topics:
            word_count[topic] = word_count.get(topic, 0) + 1

        # 阈值过滤
        filtered = {
            k: v for k, v in word_count.items() if v >= self.CONFIG["threshold"]
        }

        # 排序取前K
        sorted_topics = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
        top_topics = sorted_topics[: self.CONFIG["top_k"]]

        # 存入向量库
        stored = []
        for topic, count in top_topics:
            doc_id = vector_manager.add_knowledge(
                f"热门话题: {topic} (出现{count}次)",
                category="hot_topic",
                metadata={
                    "topic": topic,
                    "frequency": count,
                    "platforms": platforms,
                    "collected_at": datetime.now().isoformat(),
                },
            )
            stored.append({"topic": topic, "frequency": count, "vector_id": doc_id})

        return {
            "success": True,
            "platforms": platforms,
            "total_collected": len(all_topics),
            "filtered_count": len(filtered),
            "top_topics": top_topics,
            "stored": stored,
            "config": self.CONFIG,
            "message": f"采集完成，新增 {len(stored)} 条热门话题",
        }

    def _fetch_platform(self, platform):
        """从具体平台获取数据"""
        # 模拟数据 - 实际应接入真实API
        mock_data = {
            "weibo": [
                "人工智能",
                "ChatGPT",
                "新能源汽车",
                "华为Mate60",
                "小米汽车",
                "特斯拉降价",
            ],
            "baidu": ["AI写作", "视频生成模型", "文心一言4.0", "百度智能云"],
            "toutiao": ["大模型", "芯片突破", "半导体产业"],
        }
        return mock_data.get(platform, [])


skill = HotTopicCrawlerSkill()
