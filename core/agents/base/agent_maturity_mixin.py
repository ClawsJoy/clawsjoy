"""Agent 成熟度增强 Mixin - 可选继承，不破坏现有代码"""

import logging
import time
from functools import wraps
from typing import Dict, Any, Optional


class MaturityMixin:
    """为 Agent 增加错误处理、日志、监控能力"""

    def __init__(self):
        self._stats = {"calls": 0, "errors": 0, "total_time": 0}
        self._setup_logger()

    def _setup_logger(self):
        """设置结构化日志"""
        self.logger = logging.getLogger(f"agent.{self.name}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def safe_process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """带错误处理和监控的 process 包装器"""
        start = time.time()
        self._stats["calls"] += 1
        
        try:
            result = self.process(user_input, context)
            self.logger.info(f"process success: {user_input[:50]}")
            return result
        except Exception as e:
            self._stats["errors"] += 1
            self.logger.error(f"process failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name,
                "user_id": self.user_id
            }
        finally:
            self._stats["total_time"] += (time.time() - start)

    def get_stats(self) -> Dict:
        """获取监控统计"""
        avg_time = self._stats["total_time"] / max(self._stats["calls"], 1)
        return {
            "calls": self._stats["calls"],
            "errors": self._stats["errors"],
            "avg_time_ms": avg_time * 1000,
            "success_rate": 1 - (self._stats["errors"] / max(self._stats["calls"], 1))
        }
