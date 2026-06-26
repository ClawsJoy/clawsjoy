#!/usr/bin/env python3
"""Split Text - Split Text 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


class SplitTextSkill:
    def execute(self, params):
        text = params.get("text", "")
        separator = params.get("separator", "\n")
        parts = text.split(separator)
        return {"success": True, "parts": parts, "count": len(parts)}


skill = SplitTextSkill()
