from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""任务修复版 Agent - 强化任务识别"""

import sys
import re
import json
import requests
from pathlib import Path
from typing import Dict, Tuple


from core.lib.cross_session_memory import CrossSessionMemory


class TaskFixedAgent:
    VERSION = "6.4.0"
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.memory = CrossSessionMemory(user_id)
        self.ollama_url = "config_loader.get_ollama_url()"
        self.model = model_config.get_fast_model()
        
        # 知识库
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> dict:
        knowledge = {}
        
        arch_file = Path("docs/founder/ARCHITECT_SUMMARY.md")
        if arch_file.exists():
            knowledge["架构师"] = arch_file.read_text(encoding='utf-8')
            knowledge["架构师总结"] = arch_file.read_text(encoding='utf-8')
        
        founder_file = Path("docs/founder/CLAWSJOY_ORIGIN.md")
        if founder_file.exists():
            knowledge["创始人"] = founder_file.read_text(encoding='utf-8')
            knowledge["John"] = founder_file.read_text(encoding='utf-8')
        
        return knowledge
    
    def _classify_task(self, user_input: str) -> Tuple[str, str]:
        """强化任务识别"""
        lower = user_input.lower()
        
        # ========== 搜索任务 ==========
        search_triggers = [
            "找", "搜索", "查找", "查", "资料", "文档", "总结", "报告", 
            "介绍", "信息", "详情", "内容", "在哪", "哪里有"
        ]
        if any(kw in user_input for kw in search_triggers):
            # 提取要搜索的内容
            query = user_input
            for kw in search_triggers:
                query = query.replace(kw, "")
            query = query.strip().strip("，。？！")
            
            # 如果提取为空，用原文
            if not query or len(query) < 2:
                query = user_input
            
            return "search", query
        
        # ========== 问候 ==========
        if any(g in user_input for g in ["你好", "hi", "hello", "nihao"]):
            return "greeting", ""
        
        # ========== 自我介绍 ==========
        if re.match(r'^[我][叫][\s]*', user_input) or re.match(r'^[我][是][\s]*', user_input):
            return "self_intro", user_input
        
        # ========== 问身份 ==========
        if any(q in user_input for q in ["你是谁", "你叫什么", "你是什么"]):
            return "ask_who", ""
        
        # ========== 聊天 ==========
        return "chat", user_input
    
    def _search_knowledge(self, query: str) -> str:
        """搜索知识库"""
        print(f"   🔍 搜索关键词: '{query}'")
        
        # 关键词匹配
        for key, content in self.knowledge.items():
            if key in query or query in key:
                return content[:1500]
        
        # 模糊匹配
        for key, content in self.knowledge.items():
            if any(word in query for word in ["架构", "总结", "创始", "John"]):
                if any(word in key for word in ["架构", "创始", "John"]):
                    return content[:1500]
        
        return ""
    
    def process(self, user_input: str) -> Dict:
        task_type, task_param = self._classify_task(user_input)
        print(f"   🎯 任务识别: {task_type} -> '{task_param[:40]}'")
        
        name = self.memory.recall().get("name")
        
        if task_type == "search":
            result = self._search_knowledge(task_param)
            if result:
                response = f"找到相关资料：\n\n{result}"
            else:
                response = f"没有找到关于「{task_param}」的资料。可以试试「架构师总结」或「创始人资料」"
        
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
            # 聊天任务
            prompt = f"你是 ClawsJoy。{f'用户叫{name}。' if name else ''}用户说：{user_input}。请友好简洁回复。"
            try:
                resp = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False, "options": {"num_predict": 100}},
                    timeout=20
                )
                response = resp.json().get('response', '').strip() if resp.status_code == 200 else f"收到：{user_input[:50]}"
            except:
                response = f"收到：{user_input[:50]}"
        
        self.memory.record_interaction(user_input, response, task_type)
        return {"response": response}


if __name__ == "__main__":
    agent = TaskFixedAgent("John")
    
    print("=" * 60)
    print("任务修复版 Agent v6.4")
    print("=" * 60)
    
    tests = [
        "你好",
        "我叫 John",
        "你是谁",
        "找一下架构师的资料",
        "创始人的信息",
        "今天天气怎么样",
    ]
    
    for t in tests:
        print(f"\n👤 {t}")
        result = agent.process(t)
        print(f"🤖 {result['response']}")
        print("-" * 50)
