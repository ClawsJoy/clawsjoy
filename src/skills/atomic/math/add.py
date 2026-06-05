#!/usr/bin/env python3
"""Add - Add 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""加法技能"""


class AddSkill:
    name = "add"
    description = "两数相加"
    version = "1.0.0"
    category = "math"

    def execute(self, params):
        a = params.get("a", 0)
        b = params.get("b", 0)
        return {"success": True, "result": a + b, "expression": f"{a} + {b} = {a + b}"}


skill = AddSkill()
