from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""生命闭环 Agent - 修复版"""

import sys
import time
import json
import re
import math
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from core.lib.config_manager import config_manager

sys.path.insert(0, 'unified_config.ROOT')


class LifeCycleAgentFixed:
    """修复版 - 真正有生命的 Agent"""
    
    VERSION = "2.1.0"
    
    def __init__(self, agent_id: str = "default"):
        self.agent_id = agent_id
        self.agent_dir = Path(f"{get_data_root()}/agents/{agent_id}/life_cycle_fixed")
        self.agent_dir.mkdir(parents=True, exist_ok=True)

        self._load_state()
        self.ollama_url = "config_loader.get_ollama_url()"
        self.model = config_manager.get_model()
        self.birth_time = datetime.now()

        print(f"🎂 生命闭环 Agent {agent_id} v{self.VERSION} 诞生")
    
    def _load_state(self):
        """加载所有状态"""
        state_file = self.agent_dir / "state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                data = json.load(f)
                self.memory = data.get("memory", {"short_term": [], "long_term": [], "user": {}})
                self.stats = data.get("stats", {"total": 0, "dreaming_cycles": 0})
                self.learning = data.get("learning", {"success_rate": 0.5, "patterns": {}})
        else:
            self.memory = {"short_term": [], "long_term": [], "user": {}}
            self.stats = {"total": 0, "dreaming_cycles": 0}
            self.learning = {"success_rate": 0.5, "patterns": {}}
    
    def _save_state(self):
        with open(self.agent_dir / "state.json", 'w') as f:
            json.dump({
                "memory": self.memory,
                "stats": self.stats,
                "learning": self.learning
            }, f, indent=2, ensure_ascii=False)
    
    def _extract_user_info(self, text: str):
        """精确提取用户信息"""
        # 提取名字 - 更精确
        name_patterns = [
            r'[我][叫][\s]*([^\s，。！？]{2,4})',
            r'[我][是][\s]*([^\s，。！？]{2,4})',
            r'名字[叫是][\s]*([^\s，。！？]{2,4})'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                if name and len(name) >= 2:
                    self.memory["user"]["name"] = name
                    print(f"   📝 学到名字: {name}")
                    return

        # 提取偏好
        pref_match = re.search(r'喜欢[\s]*([^，。！？]{2,10})', text)
        if pref_match:
            pref = pref_match.group(1).strip()
            if pref and len(pref) < 15:
                self.memory["user"]["preferences"] = self.memory["user"].get("preferences", [])
                if pref not in self.memory["user"]["preferences"]:
                    self.memory["user"]["preferences"].append(pref)
                    print(f"   📝 学到偏好: {pref}")
    
    def _get_user_context(self) -> str:
        """获取用户上下文"""
        ctx = []
        if self.memory["user"].get("name"):
            ctx.append(f"用户名字: {self.memory['user']['name']}")
        if self.memory["user"].get("preferences"):
            ctx.append(f"用户偏好: {', '.join(self.memory['user']['preferences'])}")
        return '\n'.join(ctx)
    
    def _fast_response(self, user_input: str) -> tuple | None:
        """快速响应（不调用 LLM）"""
        lower = user_input.lower()
        name = self.memory["user"].get("name")

        # 问名字
        if any(q in lower for q in ["我叫什么", "我名字", "还记得我吗", "我是谁"]):
            if name:
                return (f"当然记得！你是{name}呀", "query_name")
            return ("你还没告诉我名字呢，请问怎么称呼？", "query_name")

        # 问偏好
        if any(q in lower for q in ["喜欢什么", "偏好", "我的风格"]):
            prefs = self.memory["user"].get("preferences", [])
            if prefs:
                return (f"根据记忆，你喜欢{', '.join(prefs)}", "query_pref")
            return ("你还没告诉我你的偏好呢", "query_pref")

        # Agent 列表
        if 'agent' in lower and ('有哪些' in lower or '列表' in lower):
            return ("系统有决策Agent、聊天Agent、执行Agent、采集Agent、安全Agent、分析Agent", "list_agents")

        # 生成图表
        if any(g in lower for g in ['图', '架构图']):
            return ("好的，正在生成架构图...", "generate_chart")

        return None
    
    def _llm_response(self, user_input: str) -> str:
        """LLM 响应（带用户上下文）"""
        context = self._get_user_context()
        name = self.memory["user"].get("name", "")

        prompt = f"""你是私人管家{f'，用户叫{name}' if name else ''}。
{f'用户偏好：{self.memory["user"].get("preferences", [])}' if self.memory["user"].get("preferences") else ''}

用户说："{user_input}"

要求：
1. 如果知道用户名字，直接用名字称呼
2. 回复简洁自然，不超过2句话
3. 不要啰嗦，不要说"哦"、"呢"等拖长音
4. 不知道就说不知道"""

        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "options": {"num_predict": 100, "temperature": 0.5}},
                timeout=20
            )
            if resp.status_code == 200:
                return resp.json().get('response', '').strip()
        except:
            pass
        return "让我想想..."
    
    def process(self, user_input: str) -> Dict:
        start = time.time()

        # 1. 提取信息
        self._extract_user_info(user_input)

        # 2. 快速响应或 LLM
        fast = self._fast_response(user_input)
        if fast:
            response, task = fast
            used_llm = False
        else:
            response = self._llm_response(user_input)
            task = "chat"
            used_llm = True

        # 3. 存储短期记忆
        self.memory["short_term"].append({
            "user": user_input[:200],
            "assistant": response[:200],
            "time": datetime.now().isoformat()
        })
        if len(self.memory["short_term"]) > 20:
            # 旧的转入长期记忆
            old = self.memory["short_term"].pop(0)
            if old.get("user") and len(old["user"]) > 10:
                self.memory["long_term"].append(old)

        self.stats["total"] += 1

        # 4. 梦境循环（每10次）
        if self.stats["total"] % 10 == 0 and self.stats["total"] > 0:
            self._dreaming_cycle()

        self._save_state()

        elapsed = (time.time() - start) * 1000

        return {
            "response": response,
            "task": task,
            "used_llm": used_llm,
            "time_ms": round(elapsed, 2),
            "memory": {
                "name": self.memory["user"].get("name"),
                "prefs": self.memory["user"].get("preferences", []),
                "short": len(self.memory["short_term"]),
                "long": len(self.memory["long_term"])
            }
        }
    
    def _dreaming_cycle(self):
        """梦境循环 - 记忆晋升"""
        self.stats["dreaming_cycles"] += 1
        print(f"   💭 梦境循环 #{self.stats['dreaming_cycles']}")

        # 晋升重要记忆
        promoted = 0
        for mem in self.memory["short_term"]:
            if len(mem.get("user", "")) > 20 and "?" in mem["user"]:
                self.memory["long_term"].append(mem)
                promoted += 1

        # 清理短期记忆
        if len(self.memory["short_term"]) > 15:
            self.memory["short_term"] = self.memory["short_term"][-15:]

        print(f"   ✨ 晋升 {promoted} 条记忆到长期")
    
    def get_status(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "version": self.VERSION,
            "awareness": min(1.0, self.stats["total"] / 50),
            "success_rate": self.learning["success_rate"],
            "short_term": len(self.memory["short_term"]),
            "long_term": len(self.memory["long_term"]),
            "dreaming_cycles": self.stats["dreaming_cycles"],
            "total": self.stats["total"],
            "known_user": self.memory["user"].get("name")
        }


if __name__ == "__main__":
    print("=" * 60)
    print("生命闭环 Agent 修复版 v2.1")
    print("=" * 60)
    
    agent = LifeCycleAgentFixed("life_fixed")
    
    conversations = [
        "你好",
        "我叫李华",
        "我喜欢极简风格",
        "ClawsJoy 有哪些 Agent？",
        "你还记得我叫什么吗？",
        "我喜欢什么风格？",
        "生成架构图",
        "谢谢"
    ]
    
    for msg in conversations:
        print(f"\n👤 {msg}")
        result = agent.process(msg)
        print(f"🤖 {result['response']}")
        print(f"   [记忆: 短期={result['memory']['short']}, 长期={result['memory']['long']}, 名字={result['memory']['name']}]")
    
    print("\n" + "=" * 60)
    print("📊 最终状态:")
    print(json.dumps(agent.get_status(), indent=2, ensure_ascii=False))
