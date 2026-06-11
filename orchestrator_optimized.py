#!/usr/bin/env python3
"""优化后的 Orchestrator 示例"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from typing import Optional, Tuple


class OptimizedOrchestrator:
    """优化版 Orchestrator"""

    # 模块级缓存，避免重复导入
    _llm_engine = None
    _vector_center = None
    _config_engine = None
    _rule_engine = None

    def __init__(self, user_id: str = "anonymous"):
        self.user_id = user_id
        self._load_engines()
        self._stats = {"total": 0, "hits": {}}

        # 可配置的阈值
        self.confidence_thresholds = {
            "llm": 0.3,
            "vector": 0.3,
            "config": 0.2,
            "rule": 0.0,
        }

    def _load_engines(self):
        """延迟加载引擎（只加载一次）"""
        if OptimizedOrchestrator._llm_engine is None:
            from core.lib.vector_knowledge_center import vector_knowledge_center
            from engine.semantic.engines.config_engine import config_engine
            from engine.semantic.engines.llm_engine import llm_engine
            from engine.semantic.engines.rule_engine import rule_engine

            OptimizedOrchestrator._llm_engine = llm_engine
            OptimizedOrchestrator._vector_center = vector_knowledge_center
            OptimizedOrchestrator._config_engine = config_engine
            OptimizedOrchestrator._rule_engine = rule_engine

    @lru_cache(maxsize=100)
    def _cached_llm_understand(self, message: str) -> Tuple[Optional[str], float]:
        """带缓存的 LLM 理解"""
        try:
            intent, conf, _ = OptimizedOrchestrator._llm_engine.understand(message)
            return intent, conf
        except Exception as e:
            return None, 0.0

    def smart_route_parallel(self, message: str) -> str:
        """并行执行四引擎"""
        self._stats["total"] += 1

        engines = [
            (self._llm_understand, "llm", self.confidence_thresholds["llm"]),
            (self._vector_understand, "vector", self.confidence_thresholds["vector"]),
            (self._config_understand, "config", self.confidence_thresholds["config"]),
            (self._rule_understand, "rule", self.confidence_thresholds["rule"]),
        ]

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(func, message): name for func, name, _ in engines
            }

            for future in as_completed(futures):
                name = futures[future]
                try:
                    intent, conf = future.result(timeout=2)
                    threshold = self.confidence_thresholds[name]
                    if conf > threshold:
                        self._stats["hits"][name] = self._stats["hits"].get(name, 0) + 1
                        return self._intent_to_agent(intent)
                except Exception:
                    continue

        return "chat_agent"

    def get_stats(self) -> dict:
        """获取统计信息"""
        total = self._stats["total"]
        return {
            "total": total,
            "hits": self._stats["hits"],
            "hit_rates": (
                {
                    name: f"{count/total*100:.1f}%"
                    for name, count in self._stats["hits"].items()
                }
                if total > 0
                else {}
            ),
        }
