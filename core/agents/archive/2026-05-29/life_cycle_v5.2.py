from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""完整生命闭环 Agent v5.2 - 感知+记忆+思考+行动+学习+反思+梦境"""

import sys
import time
import json
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple, List

sys.path.insert(0, 'unified_config.ROOT')

from core.lib.cross_session_memory import CrossSessionMemory
from core.lib.metacognition import Metacognition
from core.lib.config_manager import config_manager


class LifeCycleAgentV5:
    """完整生命闭环 Agent"""
    
    VERSION = "5.2.0"
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id

        # ========== 各层初始化 ==========
        self.memory = CrossSessionMemory(user_id)      # 记忆层
        self.metacognition = Metacognition(f"agent_{user_id}")  # 反思层

        # 梦境数据
        self.dreaming_data = {
            "short_term_memories": [],
            "long_term_memories": [],
            "dream_cycles": 0,
            "last_dream": None
        }

        self.ollama_url = "config_loader.get_ollama_url()"
        self.model = config_manager.get_model()

        user_info = self.memory.recall()
        print(f"🧠 生命闭环 Agent v{self.VERSION} 启动")
        print(f"📝 用户: {user_info.get('name', '新用户')}")
        print(f"📊 历史: {user_info.get('total_interactions', 0)} 次")
        print(f"💭 梦境周期: {self.dreaming_data['dream_cycles']}")
    
    # ========== 感知层 ==========
    def _perceive(self, text: str) -> Dict:
        """感知用户输入"""
        # 提取名字
        name_patterns = [
            r'^[我][叫][\s]*([^\s，。]{2,4})$',
            r'^[我][是][\s]*([^\s，。]{2,4})$'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text.strip())
            if match:
                name = match.group(1)
                if name not in ['什么', '谁', '怎么']:
                    self.memory.remember("name", name)
                    return {"type": "self_intro", "value": name}

        # 提取偏好
        pref_match = re.search(r'喜欢[\s]*([^，。]{2,8})$', text)
        if pref_match:
            pref = pref_match.group(1)
            if pref not in ['什么', '哪个']:
                self.memory.remember("preference", pref)
                return {"type": "preference", "value": pref}

        # 问候
        if any(g in text.lower() for g in ['你好', 'hi']):
            return {"type": "greeting"}

        # 问名字
        if any(q in text.lower() for q in ['我叫什么', '我名字', '还记得我吗']):
            return {"type": "ask_name"}

        # 问偏好
        if any(q in text.lower() for q in ['喜欢什么', '偏好']):
            return {"type": "ask_preference"}

        # Agent 列表
        if 'agent' in text.lower() and ('有哪些' in text.lower() or '列表' in text.lower()):
            return {"type": "list_agents"}

        # 生成图表
        if any(g in text.lower() for g in ['图', '架构图']):
            return {"type": "generate_chart"}

        return {"type": "chat", "text": text}
    
    # ========== 行动层 ==========
    def _act(self, perception: Dict) -> Tuple[str, str]:
        """执行行动"""
        ptype = perception.get("type")
        user_info = self.memory.recall()
        name = user_info.get("name")
        prefs = user_info.get("preferences", [])

        if ptype == "greeting":
            if name:
                return (f"你好，{name}！有什么可以帮你的？", "greeting")
            return ("你好！请问怎么称呼你？", "greeting")

        elif ptype == "self_intro":
            return (f"你好，{perception.get('value')}！很高兴认识你", "self_intro")

        elif ptype == "preference":
            return (f"好的，我记住你喜欢{perception.get('value')}", "preference")

        elif ptype == "ask_name":
            if name:
                return (f"当然记得！你是{name}呀", "query_name")
            return ("你还没告诉我名字呢", "query_name")

        elif ptype == "ask_preference":
            if prefs:
                return (f"你喜欢{', '.join(prefs)}", "query_pref")
            return ("你还没告诉我你的偏好呢", "query_pref")

        elif ptype == "list_agents":
            return ("系统有决策Agent、聊天Agent、执行Agent、采集Agent、安全Agent、分析Agent", "list_agents")

        elif ptype == "generate_chart":
            return ("正在生成架构图...", "generate_chart")

        else:
            # 复杂对话用 LLM
            return (self._think(user_info), "chat")
    
    def _think(self, user_info: Dict) -> str:
        """思考层 - LLM 推理"""
        name = user_info.get("name", "")
        prefs = user_info.get("preferences", [])

        prompt = f"""你是智能助手{f'，用户叫{name}' if name else ''}。
{f'用户偏好：{", ".join(prefs)}' if prefs else ''}

用户说："{perception.get('text', '')}"

回复要求：简洁，1-2句话。"""

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
    
    # ========== 记忆层（记录交互）==========
    def _record(self, user_input: str, response: str, task: str):
        """记录交互到记忆"""
        self.memory.record_interaction(user_input, response, task)

        # 短期记忆（用于梦境）
        self.dreaming_data["short_term_memories"].append({
            "user": user_input[:100],
            "response": response[:100],
            "task": task,
            "time": datetime.now().isoformat()
        })

        # 限制短期记忆大小
        if len(self.dreaming_data["short_term_memories"]) > 20:
            self.dreaming_data["short_term_memories"] = self.dreaming_data["short_term_memories"][-20:]
    
    # ========== 梦境层（记忆晋升）==========
    def _dream(self):
        """梦境 - 记忆晋升到长期"""
        self.dreaming_data["dream_cycles"] += 1
        self.dreaming_data["last_dream"] = datetime.now().isoformat()

        promoted = 0
        for mem in self.dreaming_data["short_term_memories"]:
            # 重要记忆晋升到长期
            if len(mem["user"]) > 20 and ("?" in mem["user"] or "叫" in mem["user"]):
                self.dreaming_data["long_term_memories"].append(mem)
                promoted += 1

        # 限制长期记忆大小
        if len(self.dreaming_data["long_term_memories"]) > 100:
            self.dreaming_data["long_term_memories"] = self.dreaming_data["long_term_memories"][-100:]

        print(f"   💭 梦境循环 #{self.dreaming_data['dream_cycles']}: 晋升 {promoted} 条记忆")
        return promoted
    
    # ========== 反思层 ==========
    def _reflect(self, user_input: str, response: str):
        """反思 - 元认知"""
        reflection = self.metacognition.reflect(user_input, response)
        quality = reflection.get('quality_score', 0.5)
        insight = reflection.get('insight', '')

        if quality < 0.5:
            print(f"   💭 反思: 回答质量偏低 ({quality:.0%})，{insight}")
        elif quality < 0.8:
            print(f"   💭 反思: 回答质量良好 ({quality:.0%})")
        else:
            print(f"   💭 反思: 回答质量优秀 ({quality:.0%})")

        return reflection
    
    # ========== 主流程 ==========
    def process(self, user_input: str) -> Dict:
        start = time.time()

        # 1. 感知
        perception = self._perceive(user_input)

        # 2. 行动（思考）
        response, task = self._act(perception)

        # 3. 记录
        self._record(user_input, response, task)

        total = self.memory.recall().get("total_interactions", 0)

        # 4. 反思（每5次）
        if total % 5 == 0 and total > 0:
            self._reflect(user_input, response)

        # 5. 梦境（每10次）
        if total % 10 == 0 and total > 0:
            self._dream()

        elapsed = (time.time() - start) * 1000

        return {
            "response": response,
            "task": task,
            "time_ms": round(elapsed, 2),
            "perception": perception["type"],
            "memory": self.memory.recall(),
            "dream_cycles": self.dreaming_data["dream_cycles"],
            "long_term_memories": len(self.dreaming_data["long_term_memories"])
        }
    
    def get_status(self) -> Dict:
        return {
            "version": self.VERSION,
            "user": self.memory.recall(),
            "metacognition": self.metacognition.get_stats(),
            "dreaming": {
                "cycles": self.dreaming_data["dream_cycles"],
                "short_term": len(self.dreaming_data["short_term_memories"]),
                "long_term": len(self.dreaming_data["long_term_memories"]),
                "last_dream": self.dreaming_data["last_dream"]
            }
        }


if __name__ == "__main__":
    print("=" * 60)
    print("完整生命闭环 Agent v5.2")
    print("=" * 60)
    print("感知 → 记忆 → 思考 → 行动 → 学习 → 反思 → 梦境")
    print("=" * 60)
    
    agent = LifeCycleAgentV5("john")
    
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
        print(f"   [感知: {result['perception']}, 记忆: {result['memory']['name']}, 梦境: {result['dream_cycles']}次]")
        print(f"   [耗时: {result['time_ms']}ms]")
    
    print("\n" + "=" * 60)
    print("📊 完整状态:")
    print(json.dumps(agent.get_status(), indent=2, ensure_ascii=False))
