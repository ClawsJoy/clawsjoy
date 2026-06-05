#!/usr/bin/env python3
"""Text Summarizer - Text Summarizer 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""文本摘要器"""


class TextSummarizerSkill:
    name = "text_summarizer"
    description = "生成文本摘要"
    version = "1.0.0"
    category = "text"

    def execute(self, params):
        text = params.get("text", "")
        max_length = params.get("max_length", 100)

        if not text:
            return {"success": False, "error": "需要提供文本"}

        if len(text) <= max_length:
            return {"success": True, "summary": text, "original_length": len(text)}

        return {
            "success": True,
            "summary": text[:max_length] + "...",
            "original_length": len(text),
        }


skill = TextSummarizerSkill()
