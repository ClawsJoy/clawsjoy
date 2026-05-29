from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""智能 Agent v5.1 - 修复名字提取"""

import sys
import time
import json
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

sys.path.insert(0, 'unified_config.ROOT')

from core.lib.metacognition import Metacognition
from core.lib.cross_session_memory import CrossSessionMemory
from core.lib.config_manager import config_manager


class IntelligentAgentV5Fixed:
    VERSION = "5.1.0"
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.metacognition = Metacognition(f"agent_{user_id}")
        self.memory = CrossSessionMemory(user_id)
        
        self.ollama_url = "config_loader.get_ollama_url()"
        self.model = config_manager.get_model()
        
        print(f"🧠 智能 Agent v{self.VERSION} 启动")
        user_info = self.memory.recall()
        print(f"📝 用户: {user_info.get('name', '新用户')}")
        print(f"📊 历史交互: {user_info.get('total_interactions', 0)} 次")
    
    def _extract_name(self, text: str) -> Optional[str]:
        """精确提取名字 - 只在明确自我介绍时"""
        # 必须是完整的自我介绍语句
        patterns = [
            r'^[我][叫][\s]*([^\s，。！？]{2,4})$',
            r'^[我][是][\s]*([^\s，。！？]{2,4})$',
            r'名字[叫是][\s]*([^\s，。！？]{2,4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text.strip())
            if match:
                name = match.group(1).strip()
                # 排除疑问词和动作词
                if name not in ['什么', '谁', '怎么', '为什么', '喜欢', '简洁', '风格']:
                    return name
        return None
    
    def _extract_preference(self, text: str) -> Optional[str]:
        """精确提取偏好"""
        # 必须是完整的偏好表达
        patterns = [
            r'喜欢[\s]*([^，。！？]{2,8})$',
            r'偏好[\s]*([^，。！？]{2,8})$',
        ]
        for pattern in patterns:
            match = re.search(pattern, text.strip())
            if match:
                pref = match.group(1).strip()
                # 排除疑问词
                if pref not in ['什么', '哪个', '怎样'] and len(pref) >= 2:
                    return pref
        return None
    
    def _fast_response(self, text: str) -> Optional[Tuple[str, str]]:
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
        if any(q in lower for q in ['我叫什么', '我名字', '我是谁', '还记得我吗']):
            if name:
                return (f"当然记得！你是{name}呀", "query_name")
            return ("你还没告诉我名字呢", "query_name")
        
        # 问偏好
        if any(q in lower for q in ['喜欢什么', '偏好', '我的风格']):
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
                timeout=20
            )
            if resp.status_code == 200:
                return resp.json().get('response', '').strip()
        except:
            pass
        return "我在思考..."
    
    def process(self, user_input: str) -> Dict:
        start = time.time()
        
        # 1. 提取名字（精确）
        name = self._extract_name(user_input)
        if name:
            self.memory.remember("name", name)
            print(f"   📝 记住名字: {name}")
        
        # 2. 提取偏好（精确）
        pref = self._extract_preference(user_input)
        if pref:
            self.memory.remember("preference", pref)
            print(f"   📝 记住偏好: {pref}")
        
        # 3. 快速响应
        fast = self._fast_response(user_input)
        if fast:
            response, task = fast
            used_llm = False
        else:
            response = self._llm_response(user_input)
            task = "chat"
            used_llm = True
        
        # 4. 记录交互
        self.memory.record_interaction(user_input, response, task)
        
        # 5. 元认知反思
        if self.memory.recall().get("total_interactions", 0) % 5 == 0:
            self.metacognition.reflect(user_input, response)
        
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
            "metacognition": self.metacognition.get_stats()
        }


if __name__ == "__main__":
    print("=" * 60)
    print("智能 Agent v5.1 - 精确提取")
    print("=" * 60)
    
    agent = IntelligentAgentV5Fixed("john_fixed")
    
    tests = [
        "你好",
        "我叫 John",
        "我喜欢简洁风格",
        "ClawsJoy 有哪些 Agent？",
        "你还记得我叫什么吗？",
        "我喜欢什么风格？",
        "生成架构图"
    ]
    
    for msg in tests:
        print(f"\n👤 {msg}")
        result = agent.process(msg)
        print(f"🤖 {result['response']}")
        print(f"   [记忆: 名字={result['memory']['name']}, 偏好={result['memory']['preferences']}]")
        print(f"   [耗时: {result['time_ms']}ms]")
    
    print("\n📊 最终状态:")
    print(json.dumps(agent.get_status(), indent=2, ensure_ascii=False))
