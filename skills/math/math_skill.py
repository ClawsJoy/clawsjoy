#!/usr/bin/env python3
"""Divide - Divide 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


class DivideSkill:
    def execute(self, params):
        b = params.get("b", 1)
        if b == 0:
            return {"success": False, "error": "除数不能为0"}
        return {"success": True, "result": params.get("a", 0) / b}


skill = DivideSkill()
