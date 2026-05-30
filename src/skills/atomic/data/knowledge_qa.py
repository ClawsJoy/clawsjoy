#!/usr/bin/env python3
"""Knowledge Qa - Knowledge Qa 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from src.lib.vector.vector_manager import vector_manager

class KnowledgeQASkill:
    name = "knowledge_qa"
    description = "基于知识库的智能问答"
    version = "1.0.0"
    category = "data"
    
    def execute(self, params):
        question = params.get("question", "")
        if not question:
            return {"success": False, "error": "需要提供问题"}
        
        # 向量检索相关知识
        results = vector_manager.search(question, top_k=5)
        
        if not results:
            return {
                "success": True,
                "answer": "知识库中没有相关信息。",
                "sources": []
            }
        
        # 构建答案
        answer = "根据知识库检索到以下相关信息：\n"
        for r in results:
            answer += f"- {r['text'][:200]}\n"
        
        return {
            "success": True,
            "question": question,
            "answer": answer,
            "sources": [{"text": r["text"][:100]} for r in results[:3]]
        }

skill = KnowledgeQASkill()
