#!/usr/bin/env python3
"""Web Fetch - Web Fetch 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""网页内容获取"""
import requests

class WebFetchSkill:
    name = "web_fetch"
    description = "获取网页内容"
    version = "1.0.0"
    category = "network"
    
    def execute(self, params):
        url = params.get("url", "")
        if not url:
            return {"success": False, "error": "需要提供 URL"}
        
        try:
            resp = requests.get(url, timeout=30)
            return {
                "success": True,
                "status_code": resp.status_code,
                "content_length": len(resp.text),
                "content_preview": resp.text[:500]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

skill = WebFetchSkill()
