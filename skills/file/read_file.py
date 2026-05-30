#!/usr/bin/env python3
"""Read File - Read File 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

class ReadFileSkill:
    def execute(self, params):
        path = params.get('path', '')
        encoding = params.get('encoding', 'utf-8')
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            return {"success": True, "content": content[:1000], "size": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}
skill = ReadFileSkill()
