#!/usr/bin/env python3
"""增强监控指标"""

import time
from collections import defaultdict
from threading import Lock

import psutil


class EnhancedMetrics:
    """增强指标收集器"""

    def __init__(self):
        self._metrics = defaultdict(list)
        self._lock = Lock()

    def record_request(self, endpoint: str, duration_ms: float, status: int):
        """记录请求"""
        with self._lock:
            self._metrics["requests_total"].append(1)
            self._metrics[f"{endpoint}_duration"].append(duration_ms)
            if status >= 400:
                self._metrics["errors_total"].append(1)
                self._metrics[f"{endpoint}_errors"].append(1)

    def get_stats(self) -> dict:
        """获取统计信息"""
        with self._lock:
            return {
                "total_requests": len(self._metrics["requests_total"]),
                "error_rate": len(self._metrics["errors_total"])
                / max(len(self._metrics["requests_total"]), 1),
                "system": {
                    "cpu": psutil.cpu_percent(),
                    "memory": psutil.virtual_memory().percent,
                    "connections": len(psutil.net_connections()),
                },
            }


metrics = EnhancedMetrics()
