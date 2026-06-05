#!/usr/bin/env python3
"""Env Var - Env Var 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import os


class EnvVarSkill:
    def execute(self, params):
        action = params.get("action", "get")
        key = params.get("key", "")
        value = params.get("value", "")
        if action == "get":
            return {"success": True, "key": key, "value": os.environ.get(key, "")}
        elif action == "set":
            os.environ[key] = value
            return {"success": True, "message": f"已设置 {key}={value}"}
        return {"success": False, "error": "无效操作"}


skill = EnvVarSkill()
