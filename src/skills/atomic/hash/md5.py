#!/usr/bin/env python3
"""Md5 - Md5 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""MD5哈希"""
import hashlib


class Md5Skill:
    name = "md5"
    description = "计算文本的 MD5 哈希值"
    version = "1.0.0"
    category = "hash"

    def execute(self, params):
        text = params.get("text", "")
        if not text:
            return {"success": False, "error": "需要提供文本"}

        result = hashlib.md5(text.encode()).hexdigest()
        return {"success": True, "md5": result, "text": text}


skill = Md5Skill()
