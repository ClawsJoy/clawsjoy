from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""生命闭环 Agent v3 - 精确提取"""

import sys
import time
import json
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple
from core.lib.config_manager import config_manager

sys.path.insert(0, 'unified_config.ROOT')


class LifeCycleAgentV3:
    """生命闭环 Agent - 精确版"""
    
    VERSION = "3.0.0"
    
    def __init__(self, agent_id: str = "default"):
        self.agent_id = agent_id
        self.agent_dir = Path(f"{get_data_root()}/agents/{agent_id}/life_v3")
        self.agent_dir.mkdir(parents=True, exist_ok=True)
        
        self._load()
        self.ollama_url = "config_loader.get_ollama_url()"
        self.model = config_manager.get_model()
        self.birth_time = datetime.now()
        
        print(f"🎂 Agent {agent_id} v{self.VERSION} 诞生")
        print(f"📝 已知用户: {self.user.get('name', '未知')}")
    
    def _load(self):
        state_file = self.agent_dir / "state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                data = json.load(f)
                self.user = data.get("user", {"name": None, "preferences": []})
                self.memory = data.get("memory", {"short": [], "long": []})
                self.stats = data.get("stats", {"total": 0, "dreams": 0})
        else:
            self.user = {"name": None, "preferences": []}
            self.memory = {"short": [], "long": []}
            self.stats = {"total": 0, "dreams": 0}
    
    def _save(self):
        with open(self.agent_dir / "state.json", 'w') as f:
            json.dump({
                "user": self.user,
                "memory": self.memory,
                "stats": self.stats
            }, f, indent=2, ensure_ascii=False)
    
    def _extract_name(self, text: str) -> Optional[str]:
        """精确提取名字 - 避免误提取"""
        # 只有在明确自我介绍时才提取
        patterns = [
            r'^[我][叫][\s]*([^\s，。！？]{2,4})$',  # "我叫李明"
            r'^[我][是][\s]*([^\s，。！？]{2,4})$',  # "我是李明"
            r'名字[叫是][\s]*([^\s，。！？]{2,4})',   # "名字叫李明"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                # 排除疑问词
                if name not in ['什么', '谁', '哪', '怎么', '为什么']:
                    return name
        return None
    
    def _extract_preference(self, text: str) -> Optional[str]:
        """提取偏好"""
        match = re.search(r'喜欢[\s]*([^，。！？]{2,8})$', text)
        if match:
            pref = match.group(1).strip()
            if pref and len(pref) < 10:
                return pref
        return None
    
    def _get_reply(self, user_input: str) -> Tuple[str, str]:
        """获取回复"""
        lower = user_input.lower()
        name = self.user.get("name")
        
        # 问候
        if any(g in lower for g in ['你好', 'hi', 'hello']):
            if name:
                return (f"你好，{name}！有什么可以帮你的？", "greeting")
            return ("你好！请问怎么称呼你？", "greeting")
        
        # 问名字
        if any(q in lower for q in ['我叫什么', '我名字', '我是谁']):
            if name:
                return (f"你是{name}呀", "query_name")
            return ("你还没告诉我名字呢", "query_name")
        
        # 问偏好
        if any(q in lower for q in ['喜欢什么', '偏好', '我的风格']):
            prefs = self.user.get("preferences", [])
            if prefs:
                return (f"你喜欢{', '.join(prefs)}", "query_pref")
            return ("你还没告诉我你的偏好呢", "query_pref")
        
        # Agent 列表
        if 'agent' in lower and ('有哪些' in lower or '列表' in lower):
            return ("系统有决策Agent、聊天Agent、执行Agent、采集Agent、安全Agent、分析Agent", "list_agents")
        
        # 生成图表
        if any(g in lower for g in ['图', '架构图']):
            return ("正在生成架构图...", "generate_chart")
        
        # 默认用 LLM
        return (self._llm_reply(user_input), "chat")
    
    def _llm_reply(self, user_input: str) -> str:
        """LLM 回复"""
        name = self.user.get("name", "")
        prefs = self.user.get("preferences", [])
        
        prompt = f"""你是私人管家{f'，用户叫{name}' if name else ''}。
{f'用户偏好：{", ".join(prefs)}' if prefs else ''}

用户：{user_input}

回复要求：简洁，1-2句话，直接回答问题。"""
        
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "options": {"num_predict": 80, "temperature": 0.3}},
                timeout=15
            )
            if resp.status_code == 200:
                return resp.json().get('response', '').strip()
        except:
            pass
        return "我在思考..."
    
    def process(self, user_input: str) -> Dict:
        start = time.time()
        
        # 1. 提取信息
        name = self._extract_name(user_input)
        if name:
            self.user["name"] = name
            print(f"   📝 学习名字: {name}")
        
        pref = self._extract_preference(user_input)
        if pref and pref not in self.user["preferences"]:
            self.user["preferences"].append(pref)
            print(f"   📝 学习偏好: {pref}")
        
        # 2. 生成回复
        response, task = self._get_reply(user_input)
        
        # 3. 存储记忆
        self.memory["short"].append({
            "user": user_input[:100],
            "assistant": response[:100],
            "time": datetime.now().isoformat()
        })
        
        # 短期记忆限制
        if len(self.memory["short"]) > 15:
            old = self.memory["short"].pop(0)
            self.memory["long"].append(old)
        
        self.stats["total"] += 1
        
        # 梦境循环
        if self.stats["total"] % 10 == 0 and self.stats["total"] > 0:
            self.stats["dreams"] += 1
            print(f"   💭 梦境 #{self.stats['dreams']}: 晋升记忆")
        
        self._save()
        
        elapsed = (time.time() - start) * 1000
        
        return {
            "response": response,
            "task": task,
            "time_ms": round(elapsed, 2),
            "memory": {
                "name": self.user["name"],
                "prefs": self.user["preferences"],
                "short": len(self.memory["short"]),
                "long": len(self.memory["long"])
            }
        }
    
    def get_status(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "version": self.VERSION,
            "name": self.user["name"],
            "preferences": self.user["preferences"],
            "short_memories": len(self.memory["short"]),
            "long_memories": len(self.memory["long"]),
            "dreams": self.stats["dreams"],
            "total": self.stats["total"]
        }


if __name__ == "__main__":
    print("=" * 60)
    print("生命闭环 Agent v3 - 精确版")
    print("=" * 60)
    
    agent = LifeCycleAgentV3("user_demo")
    
    tests = [
        "你好",
        "我叫李华",
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
        print(f"   [记忆: {result['memory']}]")
    
    print("\n" + "=" * 60)
    print("📊 最终状态:")
    print(json.dumps(agent.get_status(), indent=2, ensure_ascii=False))
