#!/usr/bin/env python3
"""Extract Keywords - Extract Keywords 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

class ExtractKeywordsSkill:
    def execute(self, params):
        text = params.get('text', '')
        import re
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', text)
        from collections import Counter
        freq = Counter(words)
        keywords = [w for w, c in freq.most_common(5)]
        return {"success": True, "keywords": keywords}
skill = ExtractKeywordsSkill()
