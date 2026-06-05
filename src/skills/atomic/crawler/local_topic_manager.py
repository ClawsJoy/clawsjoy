#!/usr/bin/env python3
"""Local Topic Manager - Local Topic Manager 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import json
import random
import sys
from datetime import datetime

from lib.smart_config import smart_config

sys.path.insert(0, "str(smart_config.ROOT)")
from src.lib.vector.vector_manager import vector_manager


class LocalTopicManagerSkill:
    name = "local_topic_manager"
    description = "本地话题管理（不依赖外部爬虫）"
    version = "1.0.0"
    category = "crawler"

    TOPIC_FILE = "data/topics/hot_topics.json"

    def execute(self, params):
        operation = params.get("operation", "get")

        if operation == "get":
            return self._get_topics(params)
        elif operation == "add":
            return self._add_topic(params)
        elif operation == "sync_to_vector":
            return self._sync_to_vector()
        elif operation == "random":
            return self._random_topics(params)

        return {"success": False, "error": "未知操作"}

    def _get_topics(self, params):
        """获取话题"""
        category = params.get("category", "all")
        limit = params.get("limit", 20)

        with open(self.TOPIC_FILE, "r") as f:
            data = json.load(f)

        if category == "all":
            all_topics = []
            for topics in data.values():
                all_topics.extend(topics)
            topics = all_topics[:limit]
        else:
            topics = data.get(category, [])[:limit]

        return {
            "success": True,
            "category": category,
            "topics": topics,
            "count": len(topics),
            "message": f"获取到 {len(topics)} 条话题",
        }

    def _add_topic(self, params):
        """添加新话题"""
        topic = params.get("topic", "")
        category = params.get("category", "tech")

        if not topic:
            return {"success": False, "error": "需要提供话题"}

        with open(self.TOPIC_FILE, "r") as f:
            data = json.load(f)

        if topic not in data[category]:
            data[category].append(topic)
            with open(self.TOPIC_FILE, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return {"success": True, "message": f"已添加话题: {topic}"}

        return {"success": True, "message": "话题已存在"}

    def _sync_to_vector(self):
        """同步到向量库"""
        with open(self.TOPIC_FILE, "r") as f:
            data = json.load(f)

        count = 0
        for category, topics in data.items():
            for topic in topics:
                vector_manager.add_knowledge(
                    f"热门话题: {topic} (分类:{category})",
                    category="hot_topic",
                    metadata={"topic": topic, "category": category, "source": "local"},
                )
                count += 1

        return {
            "success": True,
            "synced": count,
            "message": f"已同步 {count} 条话题到向量库",
        }

    def _random_topics(self, params):
        """随机获取话题"""
        count = params.get("count", 5)

        with open(self.TOPIC_FILE, "r") as f:
            data = json.load(f)

        all_topics = []
        for topics in data.values():
            all_topics.extend(topics)

        random.shuffle(all_topics)
        topics = all_topics[:count]

        return {
            "success": True,
            "topics": topics,
            "count": len(topics),
            "message": f"随机获取 {len(topics)} 条话题",
        }


skill = LocalTopicManagerSkill()
