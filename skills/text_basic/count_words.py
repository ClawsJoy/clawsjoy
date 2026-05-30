#!/usr/bin/env python3
"""Count Words - Count Words 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

class CountWordsSkill:
    def execute(self, params):
        text = params.get('text', '')
        words = text.split()
        chars = len(text)
        lines = text.count('\n') + 1
        return {"success": True, "words": len(words), "chars": chars, "lines": lines}
skill = CountWordsSkill()
