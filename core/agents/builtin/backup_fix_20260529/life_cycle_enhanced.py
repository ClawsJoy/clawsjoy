from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""增强版生命闭环 Agent - 支持 LLM 深度理解"""

import sys
import re
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple


from core.lib.cross_session_memory import CrossSessionMemory
from core.lib.metacognition import Metacognition
from core.lib.memory_vector import vector_memory


class LifeCycleEnhanced:
    VERSION = "5.4.0"
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.memory = CrossSessionMemory(user_id)
        self.metacognition = Metacognition(f"agent_{user_id}")
        
        self.ollama_url = "config_loader.get_ollama_url()"
        self.model = model_config.get_fast_model()
        self.dreaming_data = {"short_term": [], "long_term": [], "cycles": 0}
        self.interaction_count = 0
        
        user_info = self.memory.recall()
        print(f"🧠 增强版生命闭环 v{self.VERSION}")
        print(f"📝 用户: {user_info.get('name', '新用户')}")
    
    def _search_vector_memory(self, query: str) -> str:
        """搜索向量记忆库"""
        try:
            results = vector_memory.search(query, n=3)
            if results:
                return "\n".join([r.get('text', '')[:200] for r in results])
        except:
            pass
        return ""
    
    def _call_llm(self, user_input: str, context: str = "") -> str:
        """调用 LLM 深度理解"""
        name = self.memory.recall().get("name", "")
        prefs = self.memory.recall().get("preferences", [])
        
        prompt = f"""你是 ClawsJoy 智能助手，不是 Qwen 或其他模型。

{f'用户叫{name}，' if name else ''}
{f'用户偏好：{", ".join(prefs)}' if prefs else ''}

{f'相关信息：{context}' if context else ''}

用户说："{user_input}"

请友好回复。记住你是 ClawsJoy。回复简洁自然。"""
        
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "options": {"num_predict": 150, "temperature": 0.5}},
                timeout=unified_config.get("timeouts.default", 30)
            )
            if resp.status_code == 200:
                return resp.json().get('response', '').strip()
        except Exception as e:
            print(f"LLM 调用失败: {e}")
        return ""
    
    def process(self, user_input: str) -> Dict:
        self.interaction_count += 1
        
        # 1. 规则快速响应
        lower = user_input.lower()
        name = self.memory.recall().get("name")
        
        # 问候
        if any(g in lower for g in ['你好', 'hi']):
            response = f"你好{f'，{name}' if name else ''}！我是 ClawsJoy，有什么可以帮你的？"
            task = "greeting"
        # 问身份
        elif '你是谁' in lower or '你叫什么' in lower:
            response = "我是 ClawsJoy，你的智能助手！"
            task = "identity"
        # 问名字
        elif any(q in lower for q in ['我叫什么', '我名字', '我是谁']):
            response = f"你是{name}呀" if name else "我是 ClawsJoy，你还没告诉我名字呢"
            task = "ask_name"
        # 自我介绍
        elif re.match(r'^[我][叫][\s]*([^\s，。]{2,4})$', user_input.strip()):
            match = re.search(r'叫[\s]*([^\s，。]{2,4})', user_input)
            if match:
                self.memory.remember("name", match.group(1))
            response = f"你好，{match.group(1)}！我是 ClawsJoy"
            task = "self_intro"
        # Agent 列表
        elif 'agent' in lower and ('有哪些' in lower or '列表' in lower):
            response = "系统有决策Agent、聊天Agent、执行Agent、采集Agent、安全Agent、分析Agent"
            task = "list_agents"
        # 搜索向量记忆
        elif any(k in lower for k in ['找一下', '搜索', '查找', '记忆']):
            context = self._search_vector_memory(user_input)
            response = self._call_llm(user_input, context)
            task = "search"
        # 复杂对话 - 调用 LLM
        else:
            response = self._call_llm(user_input)
            task = "chat"
        
        # 记录
        self.memory.record_interaction(user_input, response, task)
        self.dreaming_data["short_term"].append({"user": user_input[:100], "response": response[:100], "time": datetime.now().isoformat()})
        
        # 梦境 (每10次)
        if self.interaction_count % 10 == 0:
            self.dreaming_data["cycles"] += 1
            print(f"   💭 梦境循环 #{self.dreaming_data['cycles']}")
        
        return {"response": response, "task": task}
    

if __name__ == "__main__":
    agent = LifeCycleEnhanced("test")
    print(agent.process("你好"))
    print(agent.process("ClawsJoy 是什么"))
