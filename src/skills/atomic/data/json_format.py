#!/usr/bin/env python3
"""Json Format - Json Format 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""JSON 格式化"""
import json


class JsonFormatSkill:
    name = "json_format"
    description = "JSON 格式化输出"
    version = "1.0.0"
    category = "data"

    def execute(self, params):
        data = params.get("data", {})
        indent = params.get("indent", 2)

        try:
            if isinstance(data, str):
                data = json.loads(data)
            result = json.dumps(data, ensure_ascii=False, indent=indent)
            return {"success": True, "formatted": result, "original": data}
        except Exception as e:
            return {"success": False, "error": str(e)}


skill = JsonFormatSkill()
