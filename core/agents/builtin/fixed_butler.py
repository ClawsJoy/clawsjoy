import logging

from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""修复版私人管家 - 真正靠谱"""

import sys
import time
import json
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from core.lib.config_manager import config_manager



class FixedButler:
    """靠谱的私人管家"""
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.user_dir = Path(funified_config.get("paths.users_dir", f"{get_data_root()}/users/") + "/{user_id}/butler_fixed")
        self.user_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory_file = self.user_dir / "memory.json"
        self.memory = self._load_memory()
        
        self.ollama_url = "config_loader.get_ollama_url()"
        self.model = config_manager.get_model()
    
    def _load_memory(self) -> Dict:
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {
            "name": None,
            "preferences": {},
            "history": [],
            "conversation_count": 0
        }
    
    def _save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def _extract_name(self, text: str) -> Optional[str]:
        """精确提取名字"""
        # 模式：我叫XXX / 我是XXX / 名字叫XXX
        patterns = [
            r'[我][叫][\s]*([^\s，。！？]{2,4})',
            r'[我][是][\s]*([^\s，。！？]{2,4})',
            r'名字[叫是][\s]*([^\s，。！？]{2,4})',
            r'称呼我[\s]*([^\s，。！？]{2,4})'
        ]
        for p in patterns:
            match = re.search(p, text)
            if match:
                name = match.group(1).strip()
                # 过滤掉常见非名字词
                if name not in ['什么', '风格', '时候', '哪里']:
                    return name
        return None
    
    def _extract_preference(self, text: str) -> Optional[str]:
        """精确提取偏好"""
        patterns = [
            r'喜欢[\s]*([^，。！？]{2,10})',
            r'偏好[\s]*([^，。！？]{2,10})'
        ]
        for p in patterns:
            match = re.search(p, text)
            if match:
                pref = match.group(1).strip()
                # 过滤掉问题句
                if '?' not in pref and '吗' not in pref and len(pref) < 10:
                    return pref
        return None
    
    def _greet(self) -> str:
        """智能问候"""
        name = self.memory.get("name")
        hour = datetime.now().hour
        
        if hour < 12:
            time_word = "早上好"
        elif hour < 18:
            time_word = "下午好"
        else:
            time_word = "晚上好"
        
        if name:
            return f"{time_word}，{name}！很高兴又见到你，今天想聊点什么？"
        return f"{time_word}！我是你的私人管家，请问怎么称呼你？"
    
    def _fast_response(self, user_input: str) -> Optional[tuple]:
        """快速响应"""
        lower = user_input.lower()
        name = self.memory.get("name")
        
        # 问候
        if any(g in lower for g in ['你好', 'hi', 'hello', '嗨']):
            return (self._greet(), "greeting")
        
        # 问名字
        if any(q in lower for q in ['我叫什么', '我名字', '还记得我吗', '我是谁']):
            if name:
                return (f"当然记得！你是{name}呀", "query_name")
            return ("你还没告诉我名字呢，请问怎么称呼？", "query_name")
        
        # 问偏好
        if any(q in lower for q in ['喜欢什么', '偏好', '我的风格']):
            prefs = self.memory.get("preferences", {})
            if prefs:
                pref_list = list(prefs.keys())
                return (f"根据我们的对话，你喜欢{', '.join(pref_list)}", "query_pref")
            return ("你还没告诉我你的偏好呢，比如喜欢什么风格？", "query_pref")
        
        # Agent 列表
        if 'agent' in lower and ('有哪些' in lower or '列表' in lower):
            agents = "决策Agent、聊天Agent、执行Agent、采集Agent、安全Agent、分析Agent"
            return (f"系统有这些Agent：{agents}，需要我详细介绍哪个？", "list_agents")
        
        # 生成图表
        if any(g in lower for g in ['图', '架构图', '蓝图']):
            return ("好的，马上为你生成架构图...", "generate_chart")
        
        # 技能
        if '技能' in lower:
            return ("系统有20+原子技能，包括图像生成、视频制作、任务调度等。想了解哪个？", "list_skills")
        
        return None
    
    def process(self, user_input: str) -> Dict:
        start = time.time()
        
        # 1. 提取名字
        name = self._extract_name(user_input)
        if name:
            self.memory["name"] = name
            self._save_memory()
        
        # 2. 提取偏好
        pref = self._extract_preference(user_input)
        if pref:
            self.memory["preferences"][pref] = True
            self._save_memory()
        
        # 3. 快速响应
        fast = self._fast_response(user_input)
        
        if fast:
            response, task = fast
            used_llm = False
        else:
            # 4. LLM 响应（带上下文）
            name = self.memory.get("name", "")
            prompt = f"""你是私人管家{f'，用户叫{name}' if name else ''}。

用户说："{user_input}"

要求：
1. {f'称呼用户{name}' if name else '问用户名字'}
2. 回复简洁自然，不超过2句话
3. 不知道就说不知道"""
            
            try:
                resp = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False, "options": {"num_predict": 150}},
                    timeout=20
                )
                response = resp.json().get('response', '') if resp.status_code == 200 else "让我想想"
            except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error: {e}", exc_info=True)
                response = "网络有点问题"
            task = "chat"
            used_llm = True
        
        # 记录历史
        self.memory["history"].append({
            "user": user_input[:100],
            "assistant": response[:100],
            "time": datetime.now().isoformat()
        })
        if len(self.memory["history"]) > 20:
            self.memory["history"] = self.memory["history"][-20:]
        self.memory["conversation_count"] += 1
        self._save_memory()
        
        elapsed = (time.time() - start) * 1000
        
        return {
            "response": response,
            "task": task,
            "used_llm": used_llm,
            "time_ms": round(elapsed, 2),
            "memory": {
                "name": self.memory.get("name"),
                "prefs": list(self.memory.get("preferences", {}).keys())
            }
        }


if __name__ == "__main__":
    print("=" * 60)
    print("👔 靠谱私人管家 - 真正记住你")
    print("=" * 60)
    
    butler = FixedButler("test_user")
    
    # 真实对话测试
    tests = [
        "你好",
        "我叫李明",
        "我喜欢简洁风格",
        "ClawsJoy 有哪些 Agent？",
        "你还记得我叫什么吗？",
        "我喜欢什么风格？",
        "生成架构图",
        "谢谢"
    ]
    
    for msg in tests:
        print(f"\n👤 我: {msg}")
        result = butler.process(msg)
        print(f"👔 管家: {result['response']}")
        print(f"   📝 记住: 名字={result['memory']['name']}, 偏好={result['memory']['prefs']}")
        print(f"   ⚡ 耗时: {result['time_ms']}ms")
    
    print("\n" + "=" * 60)
    print("最终记忆:")
    print(f"  名字: {butler.memory.get('name')}")
    print(f"  偏好: {list(butler.memory.get('preferences', {}).keys())}")
    print(f"  对话次数: {butler.memory.get('conversation_count')}")
