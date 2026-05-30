"""增强版 LLM 客户端 - 支持缓存、重试、降级"""

import requests
import time
import hashlib
from typing import Dict, Optional
from functools import wraps


class EnhancedLLMClient:
    """增强版 LLM 客户端"""
    
    def __init__(self):
        self.url = "http://localhost:11434/api/generate"
        self.model = config_helper.get_llm_model(fast=True)
        self.cache = {}
        self.max_retries = 3
    
    def _cache_key(self, prompt: str) -> str:
        return hashlib.md5(prompt.encode()).hexdigest()[:16]
    
    def generate(self, prompt: str, temperature: float = 0.7, use_cache: bool = True) -> str:
        """生成响应，带缓存和重试"""
        # 缓存检查
        if use_cache:
            key = self._cache_key(prompt)
            if key in self.cache:
                cached, ts = self.cache[key]
                if time.time() - ts < 3600:  # 1小时缓存
                    return cached

        # 重试机制
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": temperature}
                    },
                    timeout=config_helper.get_timeout("default")
                )
                if response.status_code == 200:
                    result = response.json().get('response', '')
                    if use_cache:
                        self.cache[key] = (result, time.time())
                    return result
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return self._fallback(prompt)
                time.sleep(1)

        return self._fallback(prompt)
    
    def _fallback(self, prompt: str) -> str:
        """降级响应"""
        return "服务暂时不可用，请稍后重试"


# 全局实例
llm_enhanced = EnhancedLLMClient()
