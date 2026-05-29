"""监控和日志模块"""

import time
from datetime import datetime
from typing import Dict, List
from collections import deque
from functools import wraps


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics: Dict[str, deque] = {}
        self.max_history = 100
    
    def record(self, name: str, value: float, tags: Dict = None):
        """记录指标"""
        if name not in self.metrics:
            self.metrics[name] = deque(maxlen=self.max_history)
        self.metrics[name].append({
            "value": value,
            "tags": tags or {},
            "timestamp": datetime.now().isoformat()
        })
    
    def get(self, name: str, last_n: int = 10) -> List[Dict]:
        """获取指标"""
        if name not in self.metrics:
            return []
        return list(self.metrics[name])[-last_n:]
    
    def get_average(self, name: str, last_n: int = 10) -> float:
        """获取平均值"""
        values = self.metrics.get(name, [])
        if not values:
            return 0
        recent = list(values)[-last_n:]
        return sum(v["value"] for v in recent) / len(recent)
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            name: {
                "count": len(values),
                "latest": values[-1]["value"] if values else None,
                "avg": self.get_average(name)
            }
            for name, values in self.metrics.items()
        }


class Timing:
    """性能计时装饰器"""
    
    def __init__(self, collector: MetricsCollector, name: str):
        self.collector = collector
        self.name = name
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            self.collector.record(self.name, elapsed)
            return result
        return wrapper


metrics = MetricsCollector()
