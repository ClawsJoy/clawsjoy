#!/usr/bin/env python3
"""Download File - Download File 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import requests
class DownloadFileSkill:
    def execute(self, params):
        url = params.get('url', '')
        try:
            resp = requests.get(url, timeout=30)
            return {"success": True, "size": len(resp.content), "content_type": resp.headers.get('content-type')}
        except Exception as e:
            return {"success": False, "error": str(e)}
skill = DownloadFileSkill()
