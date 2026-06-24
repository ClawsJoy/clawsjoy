#!/usr/bin/env python3
"""Llm Enhanced - 基于统一LLM客户端的增强版

@version: 5.1.0
@author: ClawsJoy
@date: 2026-6-21
"""

import hashlib
import time
from functools import wraps
from typing import Dict, Optional

from core.lib.llm_client import llm_client
from core.lib.config_helper import get_llm_endpoint, get_llm_model, get_timeout, config_helper


class EnhancedLLMClient:
    """增强版 LLM 客户端 - 缓存 + 重试 + 降级 + 统计"""

    def __init__(self):
        self.llm = llm_client
        self.model = config_helper.get_llm_model(fast=True)
        self.cache: Dict[str, tuple] = {}
        self.max_retries = 3
        self._stats = {"hits": 0, "misses": 0, "fallbacks": 0}

    def _cache_key(self, prompt: str) -> str:
        return hashlib.md5(prompt.encode()).hexdigest()[:16]

    def generate(self, prompt: str, temperature: float = 0.7,
                 use_cache: bool = True, max_tokens: int = 2048,
                 task_type: str = "default") -> str:
        """生成响应，带缓存和重试"""
        # 缓存检查
        if use_cache:
            key = self._cache_key(prompt)
            if key in self.cache:
                cached, ts = self.cache[key]
                if time.time() - ts < 3600:
                    self._stats["hits"] += 1
                    return cached

        self._stats["misses"] += 1

        # 重试机制
        for attempt in range(self.max_retries):
            try:
                result = self.llm.generate(
                    prompt=prompt,
                    model=self.model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=get_timeout("default"),
                    task_type=task_type
                )
                if result:
                    if use_cache:
                        self.cache[key] = (result, time.time())
                    return result
            except Exception as e:
                if attempt == self.max_retries - 1:
                    self._stats["fallbacks"] += 1
                    return self._fallback(prompt)
                time.sleep(1 * (attempt + 1))

        self._stats["fallbacks"] += 1
        return self._fallback(prompt)

    def _fallback(self, prompt: str) -> str:
        """降级响应"""
        return "服务暂时不可用，请稍后重试"

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self._stats,
            "cache_size": len(self.cache),
            "model": self.model,
            "hit_rate": (
                self._stats["hits"] / max(self._stats["hits"] + self._stats["misses"], 1)
            ),
        }

    def clear_cache(self):
        self.cache.clear()
        self._stats = {"hits": 0, "misses": 0, "fallbacks": 0}


# 全局实例
llm_enhanced = EnhancedLLMClient()
