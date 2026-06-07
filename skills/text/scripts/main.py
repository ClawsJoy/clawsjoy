#!/usr/bin/env python3
"""To Upper - To Upper 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


class ToUpperSkill:
    """文本转大写技能"""

    def __init__(self):
        self.name = "to_upper"
        self.version = "1.0.0"

    def execute(self, params: dict) -> dict:
        """将字符串转为大写"""
        text = params.get("text", "")
        result = text.upper()
        return {"success": True, "result": result, "message": f"'{text}' -> '{result}'"}


skill = ToUpperSkill()
