#!/usr/bin/env python3
"""List Files - List Files 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from pathlib import Path
class ListFilesSkill:
    def execute(self, params):
        directory = params.get('directory', '.')
        pattern = params.get('pattern', '*')
        path = Path(directory)
        files = [str(f) for f in path.glob(pattern) if f.is_file()]
        return {"success": True, "files": files[:50], "count": len(files)}
skill = ListFilesSkill()
