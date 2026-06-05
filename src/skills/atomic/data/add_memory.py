#!/usr/bin/env python3
"""Add Memory - Add Memory 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import sys

from lib.smart_config import smart_config

sys.path.insert(0, "str(smart_config.ROOT)")
from src.lib.vector.vector_manager import vector_manager


class AddMemorySkill:
    name = "add_memory"
    description = "添加记忆到向量库"
    version = "1.0.0"
    category = "data"

    def execute(self, params):
        text = params.get("text", "")
        memory_type = params.get("type", "general")
        importance = params.get("importance", 0.5)

        if not text:
            return {"success": False, "error": "需要提供记忆内容"}

        doc_id = vector_manager.add_memory(text, memory_type, importance)
        return {
            "success": True,
            "memory_id": doc_id,
            "text": text[:100],
            "type": memory_type,
        }


skill = AddMemorySkill()
