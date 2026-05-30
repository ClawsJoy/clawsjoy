#!/usr/bin/env python3
"""Get Time - Get Time 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""获取当前时间"""
from datetime import datetime

class GetTimeSkill:
    name = "get_time"
    description = "获取当前时间"
    version = "1.0.0"
    category = "datetime"
    
    def execute(self, params):
        format = params.get("format", "%Y-%m-%d %H:%M:%S")
        return {
            "success": True,
            "time": datetime.now().strftime(format),
            "timestamp": datetime.now().timestamp()
        }

skill = GetTimeSkill()
