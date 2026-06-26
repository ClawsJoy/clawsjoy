#!/usr/bin/env python3
"""Sort List - Sort List 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


class SortListSkill:
    def execute(self, params):
        items = params.get("items", [])
        reverse = params.get("reverse", False)
        sorted_items = sorted(items, reverse=reverse)
        return {"success": True, "sorted": sorted_items}


skill = SortListSkill()
