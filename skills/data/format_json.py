#!/usr/bin/env python3
"""Format Json - Format Json 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import json
class FormatJsonSkill:
    def execute(self, params):
        data = params.get('data', {})
        try:
            if isinstance(data, str):
                data = json.loads(data)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            return {"success": True, "result": formatted}
        except:
            return {"success": False, "error": "无效JSON"}
skill = FormatJsonSkill()
