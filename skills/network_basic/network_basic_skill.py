#!/usr/bin/env python3
"""Http Get - Http Get 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import requests


class HttpGetSkill:
    def execute(self, params):
        url = params.get("url", "")
        try:
            resp = requests.get(url, timeout=10)
            return {
                "success": True,
                "status": resp.status_code,
                "content": resp.text[:500],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


skill = HttpGetSkill()
