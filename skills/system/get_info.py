#!/usr/bin/env python3
"""Get Info - Get Info 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import platform
import os
class GetSystemInfoSkill:
    def execute(self, params):
        return {
            "success": True,
            "os": platform.system(),
            "python": platform.python_version(),
            "hostname": platform.node(),
            "cwd": os.getcwd()
        }
skill = GetSystemInfoSkill()
