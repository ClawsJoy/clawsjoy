#!/usr/bin/env python3
"""智能问答 - 基于知识库 + LLM"""

import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.simple_vector import simple_vector
from agent_core.brain_connector import brain_connector

def ask(question: str) -> str:
    # 1. 检索知识库
    results = simple_vector.search(question, top_k=3)
    
    if results:
        context = '\n'.join([r['text'][:300] for r in results if r['score'] > 0.3])
        if context:
            prompt = f"""基于以下知识回答用户问题。

知识:
{context}

问题: {question}

请简洁回答。"""
            response = brain_connector.query_llm(prompt)
            if response:
                return response
    
    # 2. 降级：直接问 LLM
    response = brain_connector.query_llm(f"请回答：{question}")
    if response:
        return response
    
    return "抱歉，暂时无法回答这个问题。"

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "ClawsJoy是什么"
    print(ask(q))
