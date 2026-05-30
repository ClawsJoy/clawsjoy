from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""记忆驱动管家 - 从系统记忆加载，不硬编码"""

import sys
import time
import json
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any
from core.lib.config_manager import config_manager



class MemoryDrivenButler:
    """记忆驱动 - 从系统记忆层读取"""
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.user_dir = Path(funified_config.get("paths.users_dir", f"{get_data_root()}/users/") + "/{user_id}/butler_memory")
        self.user_dir.mkdir(parents=True, exist_ok=True)

        # ========== 记忆驱动：所有数据从记忆加载 ==========
        self.memory_file = self.user_dir / "profile.json"
        self._load_memory()

        # 规则配置（可配置化）
        self.rules = self._load_rules()

        self.ollama_url = "config_loader.get_ollama_url()"
        self.model = config_manager.get_model()
    
    def _load_memory(self):
        """从记忆文件加载用户数据"""
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                self.profile = json.load(f)
        else:
            self.profile = {
                "user": {
                    "name": None,
                    "first_seen": datetime.now().isoformat()
                },
                "preferences": {},
                "history": [],
                "stats": {"total": 0}
            }
    
    def _save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.profile, f, indent=2, ensure_ascii=False)
    
    def _load_rules(self) -> Dict:
        """加载规则配置（从配置文件，不硬编码）"""
        rules_file = Path("config/butler_rules.json")
        if rules_file.exists():
            with open(rules_file, 'r') as f:
                return json.load(f)

        # 默认规则（可从配置修改）
        return {
            "greeting_keywords": ["你好", "hi", "hello", "嗨"],
            "name_patterns": [
                {"pattern": r'[我][叫][\s]*([^\s，。！？]{2,4})', "group": 1},
                {"pattern": r'[我][是][\s]*([^\s，。！？]{2,4})', "group": 1}
            ],
            "preference_patterns": [
                {"pattern": r'喜欢[\s]*([^，。！？]{2,10})', "group": 1}
            ],
            "query_name_keywords": ["我叫什么", "我名字", "我是谁", "还记得我吗"],
            "query_pref_keywords": ["喜欢什么", "偏好", "我的风格"],
            "fast_tasks": {
                "list_agents": {"keywords": ["agent", "Agent"], "response": "决策Agent、聊天Agent、执行Agent、采集Agent、安全Agent、分析Agent"},
                "list_skills": {"keywords": ["技能", "skill"], "response": "图像生成、视频制作、任务调度等20+原子技能"},
                "generate_chart": {"keywords": ["图", "架构图"], "response": "正在生成架构图..."}
            }
        }
    
    def _update_from_input(self, text: str):
        """从输入更新记忆（驱动学习）"""
        # 提取名字
        for pattern_cfg in self.rules.get("name_patterns", []):
            match = re.search(pattern_cfg["pattern"], text)
            if match:
                name = match.group(pattern_cfg.get("group", 1)).strip()
                if name and len(name) <= 4:
                    self.profile["user"]["name"] = name
                    self._save_memory()
                    break

        # 提取偏好
        for pattern_cfg in self.rules.get("preference_patterns", []):
            match = re.search(pattern_cfg["pattern"], text)
            if match:
                pref = match.group(pattern_cfg.get("group", 1)).strip()
                if pref and len(pref) < 15:
                    self.profile["preferences"][pref] = self.profile["preferences"].get(pref, 0) + 1
                    self._save_memory()
                    break
    
    def _get_greeting(self) -> str:
        """生成问候（基于记忆）"""
        name = self.profile["user"].get("name")
        hour = datetime.now().hour

        if hour < 12:
            time_word = "早上好"
        elif hour < 18:
            time_word = "下午好"
        else:
            time_word = "晚上好"

        if name:
            return f"{time_word}，{name}！很高兴又见到你"
        return f"{time_word}！我是你的私人管家，请问怎么称呼？"
    
    def _fast_task(self, text: str) -> Optional[tuple]:
        """快速任务（基于配置）"""
        lower = text.lower()

        # 问候
        for kw in self.rules.get("greeting_keywords", []):
            if kw in lower:
                return (self._get_greeting(), "greeting")

        # 问名字
        for kw in self.rules.get("query_name_keywords", []):
            if kw in lower:
                name = self.profile["user"].get("name")
                if name:
                    return (f"当然记得！你是{name}呀", "query_name")
                return ("你还没告诉我名字呢，请问怎么称呼？", "query_name")

        # 问偏好
        for kw in self.rules.get("query_pref_keywords", []):
            if kw in lower:
                prefs = list(self.profile["preferences"].keys())
                if prefs:
                    return (f"根据记忆，你喜欢{', '.join(prefs)}", "query_pref")
                return ("你还没告诉我你的偏好呢", "query_pref")

        # 其他任务
        for task_name, task_cfg in self.rules.get("fast_tasks", {}).items():
            for kw in task_cfg.get("keywords", []):
                if kw in lower:
                    return (task_cfg.get("response", "处理中"), task_name)

        return None
    
    def process(self, user_input: str) -> Dict:
        start = time.time()

        # 1. 从输入学习（更新记忆）
        self._update_from_input(user_input)

        # 2. 快速任务
        fast = self._fast_task(user_input)

        if fast:
            response, task = fast
            used_llm = False
        else:
            # 3. LLM 理解（上下文从记忆加载）
            name = self.profile["user"].get("name", "")
            prefs = list(self.profile["preferences"].keys())

            prompt = f"""你是私人管家{f'，用户叫{name}' if name else ''}。
{f'用户偏好：{", ".join(prefs)}' if prefs else ''}

用户说："{user_input}"

回复要求：简洁自然，1-2句话。"""

            try:
                resp = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False, "options": {"num_predict": 150}},
                    timeout=20
                )
                response = resp.json().get('response', '')
            except:
                response = "让我想想"
            task = "chat"
            used_llm = True

        # 记录历史
        self.profile["history"].append({
            "user": user_input[:100],
            "assistant": response[:100],
            "time": datetime.now().isoformat()
        })
        if len(self.profile["history"]) > 50:
            self.profile["history"] = self.profile["history"][-50:]
        self.profile["stats"]["total"] += 1
        self._save_memory()

        elapsed = (time.time() - start) * 1000

        return {
            "response": response,
            "task": task,
            "used_llm": used_llm,
            "time_ms": round(elapsed, 2),
            "memory": {
                "name": self.profile["user"].get("name"),
                "prefs": list(self.profile["preferences"].keys()),
                "total": self.profile["stats"]["total"]
            }
        }


if __name__ == "__main__":
    print("=" * 60)
    print("记忆驱动管家 - 无硬编码")
    print("=" * 60)
    
    butler = MemoryDrivenButler("user_demo")
    
    tests = [
        "你好",
        "我叫王小明",
        "我喜欢极简风格",
        "ClawsJoy 有哪些 Agent？",
        "你还记得我叫什么吗？",
        "我喜欢什么风格？",
        "生成架构图",
    ]
    
    for msg in tests:
        print(f"\n👤 {msg}")
        result = butler.process(msg)
        print(f"👔 {result['response']}")
        print(f"   📝 记忆: 名字={result['memory']['name']}, 偏好={result['memory']['prefs']}")
        print(f"   ⚡ 模式: {'规则' if not result['used_llm'] else 'LLM'}, {result['time_ms']}ms")
    
    print("\n" + "=" * 60)
    print("记忆文件:")
    print(f"  位置: data/users/user_demo/butler_memory/profile.json")
    print(f"  内容: 用户所有记忆")
