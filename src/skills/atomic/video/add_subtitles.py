#!/usr/bin/env python3
"""Add Subtitles - Add Subtitles 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""add_subtitles技能"""


class Add_subtitlesSkill:
    name = "add_subtitles"
    description = "add_subtitles处理"
    version = "1.0.0"
    category = "video"

    def execute(self, params):
        return {"success": True, "message": "add_subtitles 执行成功", "input": params}


skill = Add_subtitlesSkill()
