#!/usr/bin/env python3
"""Percentage - Percentage 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

class PercentageSkill:
    def execute(self, params):
        part = params.get('part', 0)
        whole = params.get('whole', 1)
        percentage = (part / whole) * 100 if whole != 0 else 0
        return {"success": True, "percentage": round(percentage, 2), "formatted": f"{percentage:.1f}%"}
skill = PercentageSkill()
