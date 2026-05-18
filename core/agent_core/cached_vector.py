#!/usr/bin/env python3
"""向量缓存 - 提升检索性能"""

import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from agent_core.simple_vector import simple_vector
from functools import lru_cache

class CachedVector:
    @lru_cache(maxsize=100)
    def search(self, query: str, top_k: int = 5):
        return simple_vector.search(query, top_k=top_k)
    def clear_cache(self):
        self.search.cache_clear()

cached_vector = CachedVector()
