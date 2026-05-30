#!/usr/bin/env python3
"""Sqrt - Sqrt 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import math
class SqrtSkill:
    def execute(self, params):
        num = params.get('number', 0)
        if num < 0:
            return {"success": False, "error": "不能为负数"}
        return {"success": True, "result": math.sqrt(num)}
skill = SqrtSkill()
