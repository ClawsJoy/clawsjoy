#!/usr/bin/env python3
"""Check Status - Check Status 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import requests
class CheckWebsiteSkill:
    def execute(self, params):
        url = params.get('url', '')
        try:
            resp = requests.get(url, timeout=5)
            return {"success": True, "status": resp.status_code, "online": resp.status_code == 200}
        except:
            return {"success": True, "status": 0, "online": False}
skill = CheckWebsiteSkill()
