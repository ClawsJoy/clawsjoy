#!/usr/bin/env python3
"""Parse Csv - Parse Csv 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

class ParseCsvSkill:
    def execute(self, params):
        csv_text = params.get('csv', '')
        lines = csv_text.strip().split('\n')
        headers = lines[0].split(',') if lines else []
        rows = [line.split(',') for line in lines[1:]]
        return {"success": True, "headers": headers, "rows": rows, "count": len(rows)}
skill = ParseCsvSkill()
