#!/usr/bin/env python3
"""Keyword Extractor - Keyword Extractor 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""关键词提取器"""
import re
from collections import Counter

class KeywordExtractorSkill:
    name = "keyword_extractor"
    description = "从文本中提取关键词"
    version = "1.0.0"
    category = "text"
    
    def execute(self, params):
        text = params.get("text", "")
        top_k = params.get("top_k", 5)
        
        if not text:
            return {"success": False, "error": "需要提供文本"}
        
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', text)
        words = [w for w in words if len(w) >= 2]
        word_freq = Counter(words)
        keywords = [w for w, _ in word_freq.most_common(top_k)]
        
        return {"success": True, "keywords": keywords, "total_words": len(words)}

skill = KeywordExtractorSkill()
