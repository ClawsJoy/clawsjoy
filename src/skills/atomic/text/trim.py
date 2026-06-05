#!/usr/bin/env python3
"""Trim - Trim 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""去除空格技能"""


class TrimSkill:
    name = "trim"
    description = "去除空格"
    version = "1.0.0"
    category = "text"

    def execute(self, params):
        # 基础实现
        result = {"success": True, "message": "去除空格执行成功", "input": params}

        # 特殊处理
        if "trim" == "power":
            a = params.get("a", 0)
            b = params.get("b", 1)
            result["result"] = a**b
        elif "trim" == "mod":
            a = params.get("a", 0)
            b = params.get("b", 1)
            result["result"] = a % b
        elif "trim" == "sqrt":
            import math

            a = params.get("a", 0)
            result["result"] = math.sqrt(a) if a >= 0 else 0
        elif "trim" == "abs":
            a = params.get("a", 0)
            result["result"] = abs(a)
        elif "trim" in ["to_upper", "to_lower", "trim", "reverse"]:
            text = params.get("text", "")
            if "trim" == "to_upper":
                result["result"] = text.upper()
            elif "trim" == "to_lower":
                result["result"] = text.lower()
            elif "trim" == "trim":
                result["result"] = text.strip()
            elif "trim" == "reverse":
                result["result"] = text[::-1]

        return result


skill = TrimSkill()
