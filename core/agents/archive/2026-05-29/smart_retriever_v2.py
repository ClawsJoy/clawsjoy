from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.model_config import model_config
from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""智能检索 Agent v2 - 优化搜索关键词"""

import sys
import re
import json
import requests
from pathlib import Path
from typing import Dict

sys.path.insert(0, 'unified_config.ROOT')

from core.lib.memory_vector import vector_memory
from core.lib.cross_session_memory import CrossSessionMemory


class SmartRetrieverV2:
    VERSION = "5.6.0"
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.memory = CrossSessionMemory(user_id)
        self.ollama_url = "config_loader.get_ollama_url()"
        self.model = model_config.get_fast_model()
        self.interaction_count = 0
    
    def _extract_search_keywords(self, user_input: str) -> str:
        """提取搜索关键词"""
        prompt = f"""从用户输入中提取搜索关键词，只返回关键词，不要解释。

用户说："{user_input}"

需要找的资料可能是：架构师总结、创始人资料、系统起源、开发者信息等。

返回格式：关键词1 关键词2"""

        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "options": {"num_predict": 50}},
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json().get('response', '').strip()
        except:
            pass

        # 默认提取
        keywords = re.sub(r'[找一下|帮我|搜索|查找]', '', user_input)
        return keywords.strip()
    
    def _search_vector(self, query: str) -> str:
        """搜索向量库，使用多种关键词"""
        if not query:
            return ""

        # 尝试多个关键词组合
        keywords_list = [query, query.replace("的", ""), query + " 总结", query + " 文档"]

        for keywords in keywords_list:
            try:
                results = vector_memory.search(keywords, n=3)
                if results:
                    texts = []
                    for r in results:
                        text = r.get('text', '')[:800]
                        if text and len(text) > 50:
                            texts.append(text)
                    if texts:
                        return "\n\n---\n\n".join(texts)
            except:
                pass
        return ""
    
    def _answer(self, user_input: str, context: str) -> str:
        name = self.memory.recall().get("name", "")

        prompt = f"""你是 ClawsJoy 智能助手。

{f'用户叫{name}。' if name else ''}
用户问："{user_input}"

{f'找到的资料：\n{context[:1500]}' if context else '没有找到相关资料。'}

请根据资料回答。如果有资料，直接引用内容回答。如果没有，告知用户没找到。"""

        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "options": {"num_predict": 600}},
                timeout=unified_config.get("timeouts.default", 30)
            )
            if resp.status_code == 200:
                return resp.json().get('response', '').strip()
        except:
            pass
        return "让我想想..."
    
    def process(self, user_input: str) -> Dict:
        self.interaction_count += 1
        lower = user_input.lower()
        name = self.memory.recall().get("name")

        # 规则响应
        if any(g in lower for g in ['你好', 'hi']):
            response = f"你好{f'，{name}' if name else ''}！我是 ClawsJoy"
        elif '你是谁' in lower:
            response = "我是 ClawsJoy，你的智能助手！"
        elif re.match(r'^[我][叫][\s]*([^\s，。]{2,4})$', user_input.strip()):
            match = re.search(r'叫[\s]*([^\s，。]{2,4})', user_input)
            if match:
                self.memory.remember("name", match.group(1))
            response = f"你好，{match.group(1)}！我是 ClawsJoy"
        else:
            # 搜索任务
            keywords = self._extract_search_keywords(user_input)
            print(f"   🔍 搜索关键词: {keywords}")
            context = self._search_vector(keywords)
            response = self._answer(user_input, context)

        self.memory.record_interaction(user_input, response, "chat")

        if self.interaction_count % 10 == 0:
            print(f"   💭 梦境循环 #{self.interaction_count // 10}")

        return {"response": response}


if __name__ == "__main__":
    agent = SmartRetrieverV2("John")
    
    tests = [
        "找一下架构师的总结",
        "创始人的资料",
        "关于 ClawsJoy 的起源",
    ]
    
    for t in tests:
        print(f"\n👤 {t}")
        result = agent.process(t)
        print(f"🤖 {result['response']}")
        print("-" * 50)
