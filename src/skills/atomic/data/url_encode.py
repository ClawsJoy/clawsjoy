#!/usr/bin/env python3
"""Url Encode - Url Encode 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""URL 编码"""
from urllib.parse import quote, unquote

class UrlEncodeSkill:
    name = "url_encode"
    description = "URL 编码/解码"
    version = "1.0.0"
    category = "data"
    
    def execute(self, params):
        text = params.get("text", "")
        operation = params.get("operation", "encode")
        
        if operation == "encode":
            result = quote(text, safe='')
        else:
            result = unquote(text)
        
        return {"success": True, "original": text, "result": result, "operation": operation}

skill = UrlEncodeSkill()
