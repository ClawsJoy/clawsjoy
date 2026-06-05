from core.lib.config_helper import (get_data_root, get_embedding_model,
                                    get_gateway_port, get_llm_endpoint,
                                    get_llm_model, get_timeout)

"""智能采集器 - 事件驱动 + 主动学习"""

import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from core.lib.memory_vector import vector_memory
from core.lib.smart_active_service import SmartActiveService
from core.lib.unified_config import unified_config


class SmartCollector:
    """智能采集器 - 主动、按需、智能"""

    VERSION = "2.0.0"

    def __init__(self):
        self.smart_service = SmartActiveService()
        self.running = False
        self.stats = {
            "active_collections": 0,
            "scheduled_collections": 0,
            "knowledge_added": 0,
            "last_collection": None,
        }
        print(f"🧠 智能采集器 v{self.VERSION} 已启动")

    def start(self):
        """启动智能采集"""
        self.running = True
        # 启动定时采集线程
        thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        thread.start()
        print("✅ 智能采集已启动（事件驱动 + 定时）")

    def _scheduler_loop(self):
        """调度循环 - 低峰期批量采集"""
        while self.running:
            try:
                # 凌晨2-5点批量采集
                hour = datetime.now().hour
                if 2 <= hour <= 5:
                    self._batch_collect()
                time.sleep(3600)  # 每小时检查
            except Exception as e:
                print(f"调度错误: {e}")
                time.sleep(60)

    def collect_on_demand(self, query: str, user_id: str = None) -> List[Dict]:
        """按需采集 - 用户查询触发"""
        print(f"🎯 按需采集: {query}")

        # 1. 先查本地知识库
        results = vector_memory.search(query, n=5, category="knowledge")
        if results and len(results) >= 3:
            return results

        # 2. 未命中，主动采集
        self.stats["active_collections"] += 1
        self.stats["last_collection"] = datetime.now().isoformat()

        # 3. 从种子URL采集
        collected = self._crawl_from_seeds(query)

        # 4. 向量化存储
        for item in collected:
            vector_memory.add(
                text=item.get("content", ""),
                category="knowledge",
                metadata={
                    "source": "on_demand",
                    "query": query,
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                },
            )
            self.stats["knowledge_added"] += 1

        return collected

    def _batch_collect(self):
        """批量采集 - 低峰期"""
        print(f"📦 批量采集 {datetime.now().isoformat()}")

        # 采集热门话题
        hot_topics = self._get_hot_topics()
        for topic in hot_topics:
            self.collect_on_demand(topic)

        self.stats["scheduled_collections"] += 1

    def _get_hot_topics(self) -> List[str]:
        """获取热门话题（从俱乐部、用户查询中学习）"""
        topics = []
        # 从俱乐部统计数据中提取
        try:
            with open(f"{get_data_root()}/butler_club/stats.json", "r") as f:
                import json

                stats = json.load(f)
                total = stats.get("total_interactions", 0)
                if total > 0:
                    topics.append("俱乐部成长")
                    topics.append("私人管家")
        except Exception as e:
            pass

        # 默认话题
        topics.extend(["AI智能体", "配置驱动", "多租户隔离"])
        return topics[:5]

    def _crawl_from_seeds(self, query: str) -> List[Dict]:
        """从种子URL采集"""
        results = []
        try:
            with open("config/seed_urls.json", "r") as f:
                import json

                seeds = json.load(f)

            import requests

            for category, urls in seeds.items():
                for seed in urls[:2]:  # 限制数量
                    try:
                        resp = requests.get(seed["url"], timeout=10)
                        if resp.status_code == 200:
                            results.append(
                                {
                                    "content": resp.text[:2000],
                                    "source": seed["url"],
                                    "category": category,
                                }
                            )
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"采集失败: {e}")

        return results

    def get_stats(self) -> Dict:
        """获取统计"""
        return self.stats


smart_collector = SmartCollector()
