#!/usr/bin/env python3
"""Task Aware Agent - Task Aware Agent 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import logging

from core.lib.unified_config import unified_config

#!/usr/bin/env python3
"""任务感知 Agent - 通用任务识别 + 增强检索"""

import json
import re
import sys
from typing import Dict, Tuple

import requests

from core.lib.cross_session_memory import CrossSessionMemory
from core.lib.memory_vector import vector_memory


class TaskAwareAgent:
    """
    通用任务感知 Agent
    核心：先识别任务类型，再执行，不混合
    """

    VERSION = "6.0.0"

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.memory = CrossSessionMemory(user_id)
        self.ollama_url = "config_loader.get_ollama_url()"
        self.model = model_config.get_fast_model()

    # ========== 任务识别（不依赖 LLM 的规则）==========
    def _classify_task(self, user_input: str) -> Tuple[str, str]:
        """识别任务类型，提取关键词"""
        lower = user_input.lower()

        # 1. 搜索任务
        # 关键词已统一到 config/keywords.yaml 的 agent_mapping 中
        search_keywords = []  # 由 Orchestrator 路由
        if any(kw in user_input for kw in search_keywords):
            # 提取搜索对象
            query = user_input
            for kw in search_keywords:
                query = query.replace(kw, "")
            query = query.strip().strip("，。？！")
            return "search", query if query else user_input

        # 2. 问候任务
        if any(g in user_input for g in ["你好", "hi", "hello"]):
            return "greeting", ""

        # 3. 自我介绍
        if re.match(r"^[我][叫][\s]*", user_input):
            return "self_intro", user_input

        # 4. 问身份
        if "你是谁" in user_input or "你叫什么" in user_input:
            return "ask_who", ""

        # 5. 默认聊天
        return "chat", user_input

    # ========== 增强检索 ==========
    def _search(self, query: str) -> str:
        """增强检索：多策略召回"""
        if not query:
            return ""

        results = []

        # 策略1：原文搜索
        direct = vector_memory.search(query, n=5)
        results.extend(direct)

        # 策略2：关键词扩展
        # 将用户输入拆分为关键词
        keywords = re.findall(r"[\u4e00-\u9fa5a-zA-Z]+", query)
        for kw in keywords[:3]:
            kw_results = vector_memory.search(kw, n=2)
            results.extend(kw_results)

        # 策略3：语义相近词（如果查询太短）
        if len(query) < 10:
            semantic = vector_memory.search(query + " 总结", n=3)
            results.extend(semantic)

        # 去重、排序
        seen = set()
        unique_results = []
        for r in results:
            text = r.get("text", "")[:200]
            if text and text not in seen:
                seen.add(text)
                unique_results.append(r)

        # 返回最相关的前3条
        if unique_results:
            return "\n\n---\n\n".join(
                [r.get("text", "")[:800] for r in unique_results[:3]]
            )

        return ""

    # ========== 任务执行 ==========
    def _execute_search(self, query: str) -> str:
        """执行搜索任务"""
        print(f"   🔍 执行检索: '{query}'")

        results = self._search(query)

        if results:
            # 有结果，直接返回
            return f"找到了相关资料：\n\n{results[:1500]}"
        else:
            return f"没有找到关于「{query}」的资料。可以尝试换个关键词，或者告诉我更具体的信息。"

    def _execute_greeting(self) -> str:
        name = self.memory.recall().get("name")
        return f"你好{f'，{name}' if name else ''}！我是 ClawsJoy"

    def _execute_self_intro(self, user_input: str) -> str:
        match = re.search(r"叫[\s]*([^\s，。]{2,4})", user_input)
        if match:
            name = match.group(1)
            self.memory.remember("name", name)
            return f"你好，{name}！我是 ClawsJoy"
        return "你好！请告诉我你的名字"

    def _execute_ask_who(self) -> str:
        return "我是 ClawsJoy，你的智能助手！"

    def _execute_chat(self, user_input: str) -> str:
        """聊天任务 - 调用 LLM"""
        name = self.memory.recall().get("name", "")

        prompt = f"""你是 ClawsJoy 智能助手。
{f'用户叫{name}。' if name else ''}
用户说："{user_input}"

请友好回复。"""

        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 150},
                },
                timeout=20,
            )
            if resp.status_code == 200:
                return resp.json().get("response", "").strip()
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error: {e}", exc_info=True)
            pass
        return f"收到：{user_input[:50]}"

    # ========== 主入口 ==========
    def process(self, user_input: str) -> Dict:
        # 1. 识别任务
        task_type, task_param = self._classify_task(user_input)

        print(f"   🎯 任务识别: {task_type} -> '{task_param[:30]}'")

        # 2. 执行任务
        if task_type == "search":
            response = self._execute_search(task_param)
        elif task_type == "greeting":
            response = self._execute_greeting()
        elif task_type == "self_intro":
            response = self._execute_self_intro(user_input)
        elif task_type == "ask_who":
            response = self._execute_ask_who()
        else:
            response = self._execute_chat(user_input)

        # 3. 记录
        self.memory.record_interaction(user_input, response, task_type)

        return {"response": response, "task": task_type}


if __name__ == "__main__":
    agent = TaskAwareAgent("John")

    print("=" * 60)
    print("任务感知 Agent v6.0 - 测试")
    print("=" * 60)

    tests = [
        "你好",
        "我叫 John",
        "你是谁",
        "找一下架构师的总结",
        "创始人的资料",
        "ClawsJoy 是怎么开始的",
        "今天天气怎么样",
    ]

    for t in tests:
        print(f"\n👤 {t}")
        result = agent.process(t)
        print(f"🤖 {result['response']}")
        print("-" * 40)
