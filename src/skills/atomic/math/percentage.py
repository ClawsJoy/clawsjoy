#!/usr/bin/env python3
"""Percentage - Percentage 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""百分比计算"""
class PercentageSkill:
    name = "percentage"
    description = "计算百分比"
    version = "1.0.0"
    category = "math"
    
    def execute(self, params):
        part = params.get("part", 0)
        whole = params.get("whole", 1)
        if whole == 0:
            return {"success": False, "error": "总数不能为0"}
        result = (part / whole) * 100
        return {"success": True, "percentage": round(result, 2), "part": part, "whole": whole}

skill = PercentageSkill()
