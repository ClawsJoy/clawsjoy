#!/usr/bin/env python3
"""Base64 Decode - Base64 Decode 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""Base64 解码"""
import base64


class Base64DecodeSkill:
    name = "base64_decode"
    description = "Base64 解码"
    version = "1.0.0"
    category = "encode"

    def execute(self, params):
        data = params.get("data", "")
        if not data:
            return {"success": False, "error": "需要提供编码数据"}

        try:
            decoded = base64.b64decode(data).decode()
            return {"success": True, "decoded": decoded, "original": data}
        except Exception as e:
            return {"success": False, "error": str(e)}


skill = Base64DecodeSkill()
