"""响应缓存 - 提升性能"""

import hashlib
import time
from typing import Dict, Any, Optional
from threading import Lock


class ResponseCache:
    """LRU 响应缓存"""
    
    def __init__(self, max_size: int = 100, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl  # 缓存有效期（秒）
        self.cache: Dict[str, tuple] = {}
        self.lock = Lock()
    
    def _get_key(self, user_id: str, message: str) -> str:
        """生成缓存键"""
        content = f"{user_id}:{message}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def get(self, user_id: str, message: str) -> Optional[str]:
        """获取缓存"""
        key = self._get_key(user_id, message)

        with self.lock:
            if key in self.cache:
                response, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return response
                else:
                    del self.cache[key]
        return None
    
    def set(self, user_id: str, message: str, response: str):
        """设置缓存"""
        key = self._get_key(user_id, message)

        with self.lock:
            # LRU 淘汰
            if len(self.cache) >= self.max_size:
                oldest = min(self.cache.keys(), key=lambda k: self.cache[k][1])
                del self.cache[oldest]

            self.cache[key] = (response, time.time())
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {"size": len(self.cache), "max_size": self.max_size, "ttl": self.ttl}


response_cache = ResponseCache(max_size=200, ttl=600)
