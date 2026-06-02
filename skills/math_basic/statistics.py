#!/usr/bin/env python3
"""Statistics - Statistics 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

class StatisticsSkill:
    def execute(self, params):
        numbers = params.get('numbers', [])
        if not numbers:
            return {"success": False, "error": "无数据"}
        total = sum(numbers)
        count = len(numbers)
        avg = total / count
        maximum = max(numbers)
        minimum = min(numbers)
        return {"success": True, "sum": total, "avg": avg, "max": maximum, "min": minimum, "count": count}
skill = StatisticsSkill()
