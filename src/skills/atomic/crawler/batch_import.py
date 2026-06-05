#!/usr/bin/env python3
"""Batch Import - Batch Import 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import sys

from lib.smart_config import smart_config

sys.path.insert(0, "str(smart_config.ROOT)")
from src.lib.vector.vector_manager import vector_manager


class BatchImportSkill:
    name = "batch_import"
    description = "批量导入知识到向量库"
    version = "1.0.0"
    category = "crawler"

    def execute(self, params):
        texts = params.get("texts", [])
        category = params.get("category", "general")

        if not texts:
            return {"success": False, "error": "需要提供文本列表"}

        imported = []
        for text in texts:
            if text.strip():
                doc_id = vector_manager.add_knowledge(text, category)
                imported.append({"text": text[:100], "vector_id": doc_id})

        return {
            "success": True,
            "imported_count": len(imported),
            "category": category,
            "items": imported,
        }


skill = BatchImportSkill()
