import logging

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""向量检索 Agent - 优化搜索参数"""

import sys
import re
import requests
from pathlib import Path
from typing import Dict, Tuple


from core.lib.memory_vector import vector_memory
from core.lib.cross_session_memory import CrossSessionMemory


class VectorRetriever:
    VERSION = "6.5.0"
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.memory = CrossSessionMemory(user_id)
        self.ollama_url = "config_loader.get_ollama_url()"
        self.model = model_config.get_fast_model()
    
    def _classify_task(self, user_input: str) -> Tuple[str, str]:
        lower = user_input.lower()
        
        # 搜索任务
        search_words = ["找", "搜索", "查", "资料", "文档", "总结", "报告", "介绍", "信息"]
        if any(kw in user_input for kw in search_words):
            query = user_input
            for kw in search_words:
                query = query.replace(kw, "")
            query = query.strip().strip("，。？！")
            if not query or len(query) < 2:
                query = user_input
            return "search", query
        
        if any(g in user_input for g in ["你好", "hi", "nihao"]):
            return "greeting", ""
        
        if re.match(r'^[我][叫][\s]*', user_input) or re.match(r'^[我][是][\s]*', user_input):
            return "self_intro", user_input
        
        if "你是谁" in user_input:
            return "ask_who", ""
        
        return "chat", user_input
    
    def _search_vector(self, query: str, n: int = 5) -> str:
        """向量检索 - 使用正确参数"""
        print(f"   🔍 检索: '{query}'")
        
        # 尝试多种检索策略
        all_results = []
        
        # 策略1: 原始查询
        results = vector_memory.search(query, n=n)
        all_results.extend(results)
        
        # 策略2: 如果原始查询结果少，尝试关键词拆分
        if len(results) < 2:
            keywords = re.findall(r'[\u4e00-\u9fa5]{2,}', query)
            for kw in keywords[:2]:
                kw_results = vector_memory.search(kw, n=2)
                all_results.extend(kw_results)
        
        # 去重
        seen = set()
        unique = []
        for r in all_results:
            text = r.get('text', '')[:100]
            if text and text not in seen:
                seen.add(text)
                unique.append(r)
        
        # 返回结果
        if unique:
            return "\n\n---\n\n".join([r.get('text', '')[:800] for r in unique[:3]])
        
        return ""
    
    def process(self, user_input: str) -> Dict:
        task_type, task_param = self._classify_task(user_input)
        print(f"   🎯 任务: {task_type} -> '{task_param[:40]}'")
        
        name = self.memory.recall().get("name")
        
        if task_type == "search":
            result = self._search_vector(task_param)
            if result:
                response = f"找到相关资料：\n\n{result}"
            else:
                response = f"没有找到关于「{task_param}」的资料。"
        
        elif task_type == "greeting":
            response = f"你好{f'，{name}' if name else ''}！我是 ClawsJoy"
        
        elif task_type == "self_intro":
            match = re.search(r'[叫是][\s]*([^\s，。]{2,4})', user_input)
            if match:
                self.memory.remember("name", match.group(1))
                response = f"你好，{match.group(1)}！我是 ClawsJoy"
            else:
                response = "你好！请告诉我你的名字"
        
        elif task_type == "ask_who":
            response = "我是 ClawsJoy，你的智能助手！"
        
        else:
            # 聊天
            prompt = f"你是 ClawsJoy。{f'用户叫{name}。' if name else ''}用户说：{user_input}。请友好回复。"
            try:
                resp = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False, "options": {"num_predict": 100}},
                    timeout=20
                )
                response = resp.json().get('response', '').strip() if resp.status_code == 200 else f"收到：{user_input[:50]}"
            except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error: {e}", exc_info=True)
                response = f"收到：{user_input[:50]}"
        
        self.memory.record_interaction(user_input, response, task_type)
        return {"response": response}


if __name__ == "__main__":
    agent = VectorRetriever("John")
    
    tests = [
        "你好",
        "我叫 John",
        "你是谁",
        "找一下架构师的总结",
        "创始人的资料",
    ]
    
    for t in tests:
        print(f"\n👤 {t}")
        result = agent.process(t)
        print(f"🤖 {result['response']}")
        print("-" * 50)
