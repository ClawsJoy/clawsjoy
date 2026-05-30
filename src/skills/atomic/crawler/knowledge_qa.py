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
import requests

class KnowledgeQASkill:
    name = "knowledge_qa"
    description = "基于知识库的智能问答"
    version = "1.0.0"
    category = "crawler"
    
    def execute(self, params):
        question = params.get("question", "")
        
        if not question:
            return {"success": False, "error": "需要提供问题"}
        
        # 1. 向量检索相关知识
        relevant = vector_manager.search(question, top_k=5)
        
        if not relevant:
            return {
                "success": True,
                "answer": "抱歉，知识库中没有相关信息。",
                "sources": []
            }
        
        # 2. 构建上下文
        context = "\n".join([f"- {r['text'][:500]}" for r in relevant])
        
        # 3. 调用 LLM 生成答案
        prompt = f"""基于以下知识回答问题：

相关知识：
{context}

问题：{question}

请用简洁的语言回答。如果知识不足，请说明。"""
        
        try:
            resp = requests.post(f"http://{smart_config.HOST}:{smart_config.get_port("ollama")}/api/generate",
                json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False}, timeout=30)
            answer = resp.json().get("response", "无法生成答案")
        except:
            answer = "基于检索到的知识：" + context[:300]
        
        return {
            "success": True,
            "question": question,
            "answer": answer,
            "sources": [{"text": r["text"][:100], "similarity": r["similarity"]} for r in relevant[:3]]
        }

skill = KnowledgeQASkill()
