#!/usr/bin/env python3
"""Remove Spaces - Remove Spaces 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""去除空格"""
class RemoveSpacesSkill:
    name = "remove_spaces"
    description = "去除文本中的空格"
    version = "1.0.0"
    category = "text"
    
    def execute(self, params):
        text = params.get("text", "")
        result = text.replace(" ", "")
        return {"success": True, "original": text, "result": result}

skill = RemoveSpacesSkill()
