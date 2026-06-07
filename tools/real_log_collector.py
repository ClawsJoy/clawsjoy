#!/usr/bin/env python3
"""日志收集器 - 简化版"""


class RealLogCollector:
    def collect_agent_logs(self, agent_name, hours=24):
        return []

    def get_performance_stats(self, agent_name, hours=24):
        return {"total": 0, "success_rate": 1.0}
