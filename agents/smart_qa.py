#!/usr/bin/env python3
"""智能问答 - 先检索知识库，再生成回答"""

import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.simple_vector import simple_vector
from agent_core.brain_connector import brain_connector

def ask(question: str) -> str:
    # 1. 先从知识库检索
    results = simple_vector.search(question, top_k=5)
    
    knowledge = []
    for r in results:
        if r['score'] > 0.3:
            knowledge.append(r['text'][:500])
    
    if knowledge:
        # 2. 基于知识库回答
        context = '\n\n'.join(knowledge[:3])
        prompt = f"""基于以下知识回答用户问题。

知识库内容:
{context}

用户问题: {question}

请基于以上知识回答。如果知识足够，直接回答；如果不足，可以补充说明。"""
        
        response = brain_connector.query_llm(prompt)
        if response:
            # 标记来源
            return f"📚 基于知识库回答:\n{response}"
    
    # 3. 知识库不足，直接问 LLM
    response = brain_connector.query_llm(f"请回答：{question}")
    if response:
        return f"🤖 通用回答:\n{response}"
    
    return "抱歉，暂时无法回答这个问题。"

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "ClawsJoy是什么"
    print(ask(q))
