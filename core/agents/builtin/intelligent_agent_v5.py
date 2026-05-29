import logging

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""智能 Agent v5.0 - 元认知 + 跨会话记忆 + 生命闭环"""

import sys
import time
import json
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple


from core.lib.metacognition import Metacognition
from core.lib.cross_session_memory import CrossSessionMemory
from core.lib.memory_vector import vector_memory
from core.lib.config_manager import config_manager


class IntelligentAgentV5:
    """完整智能 Agent - 元认知 + 跨会话记忆"""
    
    VERSION = "5.0.0"
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.metacognition = Metacognition(f"agent_{user_id}")
        self.memory = CrossSessionMemory(user_id)
        
        self.ollama_url = "config_loader.get_ollama_url()"
        self.model = config_manager.get_model()
        self.birth_time = datetime.now()
        
        print(f"🧠 智能 Agent v{self.VERSION} 启动")
        print(f"📝 用户: {self.memory.recall().get('name', '新用户')}")
        print(f"📊 历史交互: {self.memory.recall().get('total_interactions', 0)} 次")
    
    def _extract_info(self, text: str):
        """提取用户信息"""
        # 名字
        name_match = re.search(r'[我叫我是][\s]*([^\s，。]{2,4})', text)
        if name_match:
            name = name_match.group(1)
            if name not in ['什么', '谁', '怎么']:
                self.memory.remember("name", name)
                print(f"   📝 记住名字: {name}")
        
        # 偏好
        pref_match = re.search(r'喜欢[\s]*([^，。]{2,10})', text)
        if pref_match:
            pref = pref_match.group(1)
            self.memory.remember("preference", pref)
            print(f"   📝 记住偏好: {pref}")
    
    def _fast_response(self, text: str) -> Optional[Tuple[str, str]]:
        """快速响应"""
        lower = text.lower()
        user_info = self.memory.recall()
        name = user_info.get("name")
        prefs = user_info.get("preferences", [])
        
        # 问候
        if any(g in lower for g in ['你好', 'hi']):
            if name:
                return (f"你好，{name}！有什么可以帮你的？", "greeting")
            return ("你好！请问怎么称呼你？", "greeting")
        
        # 问名字
        if any(q in lower for q in ['我叫什么', '我名字', '我是谁']):
            if name:
                return (f"你是{name}呀", "query_name")
            return ("你还没告诉我名字呢", "query_name")
        
        # 问偏好
        if any(q in lower for q in ['喜欢什么', '偏好']):
            if prefs:
                return (f"你喜欢{', '.join(prefs)}", "query_pref")
            return ("你还没告诉我你的偏好呢", "query_pref")
        
        # Agent 列表
        if 'agent' in lower and ('有哪些' in lower or '列表' in lower):
            return ("系统有决策Agent、聊天Agent、执行Agent、采集Agent、安全Agent、分析Agent", "list_agents")
        
        # 生成图表
        if any(g in lower for g in ['图', '架构图']):
            return ("正在生成架构图...", "generate_chart")
        
        return None
    
    def _llm_response(self, text: str) -> str:
        """LLM 响应"""
        user_info = self.memory.recall()
        name = user_info.get("name", "")
        prefs = user_info.get("preferences", [])
        
        prompt = f"""你是智能助手{f'，用户叫{name}' if name else ''}。
{f'用户偏好：{", ".join(prefs)}' if prefs else ''}

用户说："{text}"

回复要求：简洁，1-2句话，直接回答问题。"""
        
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "options": {"num_predict": 100, "temperature": 0.3}},
                timeout=15
            )
            if resp.status_code == 200:
                return resp.json().get('response', '').strip()
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error: {e}", exc_info=True)
            pass
        return "我在思考..."
    
    def process(self, user_input: str) -> Dict:
        start = time.time()
        
        # 1. 提取信息
        self._extract_info(user_input)
        
        # 2. 快速响应或 LLM
        fast = self._fast_response(user_input)
        if fast:
            response, task = fast
            used_llm = False
        else:
            response = self._llm_response(user_input)
            task = "chat"
            used_llm = True
        
        # 3. 记录交互
        self.memory.record_interaction(user_input, response, task)
        
        # 4. 元认知反思（每5次）
        if self.memory.recall().get("total_interactions", 0) % 5 == 0:
            reflection = self.metacognition.reflect(user_input, response)
            print(f"   💭 反思: {reflection['insight']}")
        
        # 5. 自我进化（每20次）
        if self.memory.recall().get("total_interactions", 0) % 20 == 0 and self.memory.recall().get("total_interactions", 0) > 0:
            evolution = self.metacognition.evolve()
            print(f"   🧬 进化: {evolution.get('suggestions', ['继续优化'])[0]}")
        
        # 6. 存储到向量库（重要记忆）
        if any(k in user_input for k in ["记住", "重要", "我叫"]):
            vector_memory.add(
                f"用户{self.user_id}: {user_input}\n回复: {response}",
                category=f"user_{self.user_id}_important"
            )
        
        elapsed = (time.time() - start) * 1000
        
        return {
            "response": response,
            "task": task,
            "used_llm": used_llm,
            "time_ms": round(elapsed, 2),
            "memory": self.memory.recall()
        }
    
    def get_status(self) -> Dict:
        return {
            "version": self.VERSION,
            "user": self.memory.recall(),
            "metacognition": self.metacognition.get_stats(),
            "birth": self.birth_time.isoformat()
        }


if __name__ == "__main__":
    print("=" * 60)
    print("智能 Agent v5.0 - 元认知 + 跨会话记忆")
    print("=" * 60)
    
    agent = IntelligentAgentV5("john")
    
    # 模拟对话
    tests = [
        "你好",
        "我叫 John",
        "我喜欢简洁风格",
        "ClawsJoy 有哪些 Agent？",
        "你还记得我叫什么吗？",
        "我喜欢什么风格？"
    ]
    
    for msg in tests:
        print(f"\n👤 {msg}")
        result = agent.process(msg)
        print(f"🤖 {result['response']}")
        print(f"   [任务: {result['task']}, 耗时: {result['time_ms']}ms]")
    
    print("\n" + "=" * 60)
    print("📊 Agent 状态:")
    print(json.dumps(agent.get_status(), indent=2, ensure_ascii=False))
