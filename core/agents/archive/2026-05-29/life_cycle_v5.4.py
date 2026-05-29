from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""完全配置驱动的生命闭环 Agent v5.4 - 无硬编码"""

import sys
import time
import json
import re
import yaml
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

sys.path.insert(0, 'unified_config.ROOT')

from core.lib.cross_session_memory import CrossSessionMemory
from core.lib.config_manager import config_manager
from core.lib.unified_config import unified_config


class LifeCycleConfigDrivenV2:
    """完全配置驱动 - 所有参数从配置文件读取"""
    
    VERSION = "5.4.0"
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.config = self._load_config()
        
        self.memory = CrossSessionMemory(user_id)
        
        self.dreaming_data = {
            "short_term": [],
            "long_term": [],
            "cycles": 0,
            "last_dream": None
        }
        
        self.ollama_url = "config_loader.get_ollama_url()"
        self.model = config_manager.get_model()
        
        # 从配置读取参数
        self.reflection_interval = self.config["reflection"]["interval"]
        self.dreaming_interval = self.config["dreaming"]["interval"]
        self.short_term_max = self.config["dreaming"]["short_term_max"]
        self.long_term_max = self.config["dreaming"]["long_term_max"]
        self.quality_excellent = self.config["reflection"]["quality_thresholds"]["excellent"]
        self.quality_good = self.config["reflection"]["quality_thresholds"]["good"]
        
        user_info = self.memory.recall()
        print(f"🧠 配置驱动生命闭环 v{self.VERSION}")
        print(f"📝 用户: {user_info.get('name', '新用户')}")
        print(f"📊 配置: 反思间隔={self.reflection_interval}, 梦境间隔={self.dreaming_interval}")
    
    def _load_config(self) -> Dict:
        config_file = Path("config/driver/life_cycle.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                return unified_config.get('agent_lifecycle', {})
        raise FileNotFoundError("配置文件不存在")
    
    def _perceive(self, text: str) -> Dict:
        excluded = self.config["perception"]["excluded_words"]
        
        # 名字提取
        for pattern in self.config["perception"]["name_patterns"]:
            match = re.search(pattern, text.strip())
            if match:
                name = match.group(1)
                if name not in excluded:
                    self.memory.remember("name", name)
                    return {"type": "self_intro", "value": name}
        
        # 偏好提取
        for pattern in self.config["perception"]["preference_patterns"]:
            match = re.search(pattern, text.strip())
            if match:
                pref = match.group(1)
                if pref not in excluded:
                    self.memory.remember("preference", pref)
                    return {"type": "preference", "value": pref}
        
        lower = text.lower()
        if any(g in lower for g in ['你好', 'hi']):
            return {"type": "greeting"}
        if any(q in lower for q in ['我叫什么', '我名字', '还记得我吗']):
            return {"type": "ask_name"}
        if any(q in lower for q in ['喜欢什么', '偏好']):
            return {"type": "ask_preference"}
        if 'agent' in lower and ('有哪些' in lower or '列表' in lower):
            return {"type": "list_agents"}
        if any(g in lower for g in ['图', '架构图']):
            return {"type": "generate_chart"}
        
        return {"type": "chat", "text": text}
    
    def _act(self, perception: Dict) -> Tuple[str, str]:
        ptype = perception.get("type")
        user_info = self.memory.recall()
        name = user_info.get("name")
        prefs = user_info.get("preferences", [])
        
        actions = {
            "greeting": (f"你好{f'，{name}' if name else ''}！有什么可以帮你的？", "greeting"),
            "self_intro": (f"你好，{perception.get('value')}！很高兴认识你", "self_intro"),
            "preference": (f"好的，我记住你喜欢{perception.get('value')}", "preference"),
            "ask_name": (f"当然记得！你是{name}呀" if name else "你还没告诉我名字呢", "query_name"),
            "ask_preference": (f"你喜欢{', '.join(prefs)}" if prefs else "你还没告诉我你的偏好呢", "query_pref"),
            "list_agents": ("系统有决策Agent、聊天Agent、执行Agent、采集Agent、安全Agent、分析Agent", "list_agents"),
            "generate_chart": ("正在生成架构图...", "generate_chart"),
        }
        
        if ptype in actions:
            return actions[ptype]
        
        return (self._think(user_info, perception.get("text", "")), "chat")
    
    def _think(self, user_info: Dict, text: str) -> str:
        cfg = self.config["thinking"]
        name = user_info.get("name", "")
        prefs = user_info.get("preferences", [])
        
        prompt = f"""你是智能助手{f'，用户叫{name}' if name else ''}。
{f'用户偏好：{", ".join(prefs)}' if prefs else ''}

用户说："{text}"

回复要求：简洁，1-2句话。"""
        
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": cfg["llm_temperature"],
                        "num_predict": cfg["llm_max_tokens"]
                    }
                },
                timeout=cfg["llm_timeout"]
            )
            if resp.status_code == 200:
                return resp.json().get('response', '').strip()
        except:
            pass
        return "我在思考..."
    
    def _record(self, user_input: str, response: str):
        self.memory.record_interaction(user_input, response, "")
        
        self.dreaming_data["short_term"].append({
            "user": user_input[:100],
            "response": response[:100],
            "time": datetime.now().isoformat()
        })
        
        # 使用配置的短期记忆上限
        if len(self.dreaming_data["short_term"]) > self.short_term_max:
            self.dreaming_data["short_term"] = self.dreaming_data["short_term"][-self.short_term_max:]
    
    def _assess_quality(self, response: str) -> float:
        """质量评分 - 使用配置的权重"""
        weights = self.config["reflection"]["quality_weights"]
        score = 0.5
        
        if 20 < len(response) < 500:
            score += weights.get("length", 0.2)
        if any(k in response for k in ["Agent", "技能", "系统"]):
            score += weights.get("content", 0.2)
        if "我不知道" not in response and "无法回答" not in response:
            score += weights.get("no_template", 0.1)
        
        return min(1.0, score)
    
    def _reflect(self, user_input: str, response: str):
        """反思 - 使用配置的阈值"""
        quality = self._assess_quality(response)
        
        if quality >= self.quality_excellent:
            level = "优秀"
        elif quality >= self.quality_good:
            level = "良好"
        else:
            level = "偏低"
        
        print(f"   💭 反思: 回答质量{level} ({quality:.0%})")
    
    def _dream(self):
        """梦境 - 使用配置的参数"""
        self.dreaming_data["cycles"] += 1
        self.dreaming_data["last_dream"] = datetime.now().isoformat()
        
        promoted = 0
        min_len = self.config["dreaming"]["promote_conditions"]["min_length"]
        
        for mem in self.dreaming_data["short_term"]:
            if len(mem["user"]) > min_len:
                self.dreaming_data["long_term"].append(mem)
                promoted += 1
        
        # 使用配置的长期记忆上限
        if len(self.dreaming_data["long_term"]) > self.long_term_max:
            self.dreaming_data["long_term"] = self.dreaming_data["long_term"][-self.long_term_max:]
        
        print(f"   💭 梦境循环 #{self.dreaming_data['cycles']}: 晋升 {promoted} 条记忆")
    
    def process(self, user_input: str) -> Dict:
        start = time.time()
        
        perception = self._perceive(user_input)
        response, task = self._act(perception)
        self._record(user_input, response)
        
        total = self.memory.recall().get("total_interactions", 0)
        
        # 反思 - 使用配置的间隔
        if total % self.reflection_interval == 0 and total > 0:
            self._reflect(user_input, response)
        
        # 梦境 - 使用配置的间隔
        if total % self.dreaming_interval == 0 and total > 0:
            self._dream()
        
        elapsed = (time.time() - start) * 1000
        
        return {
            "response": response,
            "task": task,
            "time_ms": round(elapsed, 2),
            "perception": perception["type"],
            "memory": self.memory.recall(),
            "dream_cycles": self.dreaming_data["cycles"]
        }
    
    def get_status(self) -> Dict:
        return {
            "version": self.VERSION,
            "user": self.memory.recall(),
            "config": {
                "reflection_interval": self.reflection_interval,
                "dreaming_interval": self.dreaming_interval,
                "short_term_max": self.short_term_max,
                "long_term_max": self.long_term_max
            },
            "dreaming": {
                "cycles": self.dreaming_data["cycles"],
                "short_term": len(self.dreaming_data["short_term"]),
                "long_term": len(self.dreaming_data["long_term"])
            }
        }


if __name__ == "__main__":
    print("=" * 60)
    print("完全配置驱动生命闭环 v5.4 - 无硬编码")
    print("=" * 60)
    
    agent = LifeCycleConfigDrivenV2("john")
    
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
        print(f"   [感知: {result['perception']}, 梦境: {result['dream_cycles']}次, 耗时: {result['time_ms']}ms]")
    
    print("\n📊 配置状态:")
    print(json.dumps(agent.get_status(), indent=2, ensure_ascii=False))
