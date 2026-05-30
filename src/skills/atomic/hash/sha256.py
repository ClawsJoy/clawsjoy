#!/usr/bin/env python3
"""Sha256 - Sha256 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""SHA256哈希"""
import hashlib

class Sha256Skill:
    name = "sha256"
    description = "计算文本的 SHA256 哈希值"
    version = "1.0.0"
    category = "hash"
    
    def execute(self, params):
        text = params.get("text", "")
        if not text:
            return {"success": False, "error": "需要提供文本"}
        
        result = hashlib.sha256(text.encode()).hexdigest()
        return {"success": True, "sha256": result, "text": text}

skill = Sha256Skill()
