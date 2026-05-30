#!/usr/bin/env python3
"""Round Number - Round Number 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

class RoundNumberSkill:
    def execute(self, params):
        number = params.get('number', 0)
        decimals = params.get('decimals', 2)
        rounded = round(number, decimals)
        return {"success": True, "original": number, "rounded": rounded}
skill = RoundNumberSkill()
