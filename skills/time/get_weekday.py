#!/usr/bin/env python3
"""Get Weekday - Get Weekday 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from datetime import datetime
class GetWeekdaySkill:
    def execute(self, params):
        date_str = params.get('date', '')
        fmt = params.get('format', '%Y-%m-%d')
        dt = datetime.strptime(date_str, fmt)
        weekdays = ['一', '二', '三', '四', '五', '六', '日']
        return {"success": True, "weekday": weekdays[dt.weekday()], "is_weekend": dt.weekday() >= 5}
skill = GetWeekdaySkill()
