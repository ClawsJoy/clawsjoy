#!/usr/bin/env python3
"""时间/日期格式化技能"""

from datetime import datetime


class TimeSkill:
    name = "time"
    description = "获取当前时间或格式化日期"
    version = "1.0.0"

    def execute(self, params):
        """获取当前时间或格式化指定日期"""
        if not params:
            params = {}

        date_str = params.get("date", "")

        # 如果没有提供日期，返回当前时间
        if not date_str:
            now = datetime.now()
            return {
                "success": True,
                "result": now.strftime("%Y-%m-%d %H:%M:%S"),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
            }

        # 格式化指定日期
        from_fmt = params.get("from_format", "%Y-%m-%d")
        to_fmt = params.get("to_format", "%Y年%m月%d日")

        try:
            dt = datetime.strptime(date_str, from_fmt)
            formatted = dt.strftime(to_fmt)
            return {"success": True, "result": formatted}
        except ValueError as e:
            return {"success": False, "error": f"日期格式错误: {e}"}


skill = TimeSkill()
