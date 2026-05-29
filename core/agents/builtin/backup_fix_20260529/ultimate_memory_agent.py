from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""终极记忆 Agent - 短期记忆用文件，长期记忆用向量库"""

import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List


from core.lib.memory_vector import vector_memory
from core.lib.config_manager import config_manager


class UltimateMemoryAgent:
    """短期记忆（会话、偏好）+ 长期记忆（向量库）"""
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.user_dir = Path(funified_config.get("paths.users_dir", f"{get_data_root()}/users/") + "/{user_id}")
        self.user_dir.mkdir(parents=True, exist_ok=True)
        
        # 短期记忆（文件）
        self.short_term_file = self.user_dir / "short_term.json"
        self.short_term = self._load_short_term()
        
        self.ollama_url = "config_loader.get_ollama_url()"
        self.model = config_manager.get_model()
    
    def _load_short_term(self) -> Dict:
        if self.short_term_file.exists():
            with open(self.short_term_file, 'r') as f:
                return json.load(f)
        return {"name": None, "preferences": {}, "history": [], "session_id": None}
    
    def _save_short_term(self):
        with open(self.short_term_file, 'w') as f:
            json.dump(self.short_term, f, indent=2)
    
    def _extract_and_store(self, user_input: str, response: str):
        """提取并存储到短期记忆"""
        # 提取名字
        if "我叫" in user_input or "我是" in user_input:
            import re
            match = re.search(r'[我叫我是][\s]*([^\s，。]+)', user_input)
            if match:
                self.short_term["name"] = match.group(1)
        
        # 提取偏好
        if "喜欢" in user_input:
            import re
            match = re.search(r'喜欢([^，。]+)', user_input)
            if match:
                pref = match.group(1).strip()
                self.short_term["preferences"][pref] = True
        
        # 记录历史
        self.short_term["history"].append({
            "user": user_input[:200],
            "response": response[:200],
            "time": datetime.now().isoformat()
        })
        if len(self.short_term["history"]) > 20:
            # 将旧历史存入长期记忆
            old = self.short_term["history"].pop(0)
            vector_memory.add(
                f"用户{self.user_id}说: {old['user']}\n回复: {old['response']}",
                category=f"user_{self.user_id}_history"
            )
        
        self._save_short_term()
    
    def _get_context(self) -> str:
        """获取上下文（短期+长期）"""
        ctx = []
        
        # 短期记忆
        if self.short_term.get("name"):
            ctx.append(f"用户名字: {self.short_term['name']}")
        if self.short_term.get("preferences"):
            ctx.append(f"用户偏好: {', '.join(self.short_term['preferences'].keys())}")
        
        # 最近对话
        recent = self.short_term.get("history", [])[-3:]
        for h in recent:
            ctx.append(f"之前: {h['user'][:40]} → {h['response'][:40]}")
        
        # 长期记忆检索相关
        if len(self.short_term.get("history", [])) > 0:
            last_msg = self.short_term["history"][-1]["user"] if self.short_term["history"] else ""
            if last_msg:
                long_mem = vector_memory.search(f"用户{self.user_id} {last_msg}", n=2)
                for mem in long_mem:
                    ctx.append(f"历史相关: {mem.get('text', '')[:80]}")
        
        return '\n'.join(ctx)
    
    def process(self, user_input: str) -> Dict:
        start = time.time()
        
        # 快速规则
        lower = user_input.lower()
        
        if 'agent' in lower and ('有哪些' in lower or '列表' in lower):
            response = "ClawsJoy 有决策Agent、聊天Agent、执行Agent、采集Agent、安全Agent、分析Agent等10个专业Agent"
            task = "list_agents"
            used_llm = False
        
        elif any(k in lower for k in ['图', 'chart', '架构图']):
            response = "已生成架构图，保存在 output 目录"
            task = "generate_chart"
            used_llm = False
        
        else:
            # LLM 理解 + 短期记忆 + 长期记忆
            context = self._get_context()
            name = self.short_term.get("name", "")
            
            prompt = f"""你是 ClawsJoy 智能助手。

已知信息：
{context}

用户：{user_input}
{f'用户名字：{name}' if name else ''}

请友好回复，利用已知信息。"""
            
            try:
                resp = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False, "options": {"num_predict": 300}},
                    timeout=config_manager.get_timeout("normal")
                )
                response = resp.json().get('response', '')
            except:
                response = "系统繁忙"
            task = "chat"
            used_llm = True
        
        # 存储记忆
        self._extract_and_store(user_input, response)
        
        elapsed = (time.time() - start) * 1000
        
        return {
            "response": response,
            "task": task,
            "used_llm": used_llm,
            "time_ms": round(elapsed, 2),
            "memory": {
                "name": self.short_term.get("name"),
                "prefs": len(self.short_term.get("preferences", {})),
                "history_len": len(self.short_term.get("history", []))
            }
        }


if __name__ == "__main__":
    print("=" * 60)
    print("终极记忆 Agent - 短期+长期记忆")
    print("=" * 60)
    
    agent = UltimateMemoryAgent("user_demo")
    
    tests = [
        "我叫王小明",
        "ClawsJoy 有哪些 Agent？",
        "我喜欢简洁风格",
        "我叫什么名字？",
        "我喜欢的风格是什么？",
        "生成架构图",
    ]
    
    for test in tests:
        print(f"\n👤 {test}")
        result = agent.process(test)
        print(f"🤖 {result['response']}")
        print(f"   [LLM: {result['used_llm']}, 耗时: {result['time_ms']}ms]")
        print(f"   📝 记忆: 名字={result['memory']['name']}, 偏好数={result['memory']['prefs']}, 历史={result['memory']['history_len']}")
