#!/usr/bin/env python3
"""LLM 养成管理器 - 持久化存储"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class LLMNurture:
    """LLM 养成管理器 - 持久化"""

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.data_dir = Path(f"data/nurture/{user_id}")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.profile_file = self.data_dir / "profile.json"
        self.memory_file = self.data_dir / "memories.json"
        self.stats_file = self.data_dir / "stats.json"
        
        self._load()

    def _load(self):
        """加载所有数据"""
        # 加载画像
        if self.profile_file.exists():
            with open(self.profile_file, 'r') as f:
                self.profile = json.load(f)
        else:
            self.profile = {
                "created_at": datetime.now().isoformat(),
                "name": None,
                "preferences": {},
                "interaction_count": 0
            }
        
        # 加载记忆
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                self.memories = json.load(f)
        else:
            self.memories = []
        
        # 加载统计
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                "total_interactions": 0,
                "successful": 0,
                "failed": 0,
                "agent_usage": {},
                "skills_used": {}
            }

    def _save(self):
        """保存所有数据"""
        with open(self.profile_file, 'w') as f:
            json.dump(self.profile, f, indent=2, ensure_ascii=False)
        with open(self.memory_file, 'w') as f:
            json.dump(self.memories[-100:], f, indent=2, ensure_ascii=False)
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)

    def record_interaction(self, user_input: str, response: str, success: bool, agent: str = None):
        """记录交互"""
        self.stats["total_interactions"] += 1
        if success:
            self.stats["successful"] += 1
        else:
            self.stats["failed"] += 1
        
        if agent:
            self.stats["agent_usage"][agent] = self.stats["agent_usage"].get(agent, 0) + 1
        
        # 记录记忆
        self.memories.append({
            "input": user_input[:200],
            "response": response[:200],
            "success": success,
            "agent": agent,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save()

    def record_preference(self, key: str, value: str):
        """记录用户偏好"""
        self.profile["preferences"][key] = value
        self._save()

    def get_user_name(self) -> Optional[str]:
        return self.profile.get("name")

    def set_user_name(self, name: str):
        self.profile["name"] = name
        self._save()

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats

    def get_memories(self, limit: int = 10) -> List:
        return self.memories[-limit:]

    def get_profile(self) -> Dict:
        return self.profile

    def get_nurture_prompt(self) -> str:
        """生成养成提示词"""
        # 用户偏好
        prefs = self.profile.get("preferences", {})
        pref_text = "\n".join([f"- {k}: {v}" for k, v in prefs.items()]) if prefs else "暂无"

        # 常用 Agent
        agent_usage = self.stats.get("agent_usage", {})
        top_agents = sorted(agent_usage.items(), key=lambda x: x[1], reverse=True)[:3]
        agent_text = ", ".join([f"{a}({c}次)" for a, c in top_agents]) if top_agents else "暂无"

        return f"""
【用户画像】
- 名字: {self.profile.get('name', '未设置')}
- 交互次数: {self.stats.get('total_interactions', 0)}
- 成功次数: {self.stats.get('successful', 0)}
- 常用 Agent: {agent_text}

【用户偏好】
{pref_text}

【最近记忆】
{self._format_recent_memories(3)}
"""

    def _format_recent_memories(self, n: int) -> str:
        recent = self.memories[-n:] if self.memories else []
        if not recent:
            return "暂无"
        lines = []
        for m in recent:
            status = "✅" if m.get("success") else "❌"
            input_text = m.get("input", "")[:50]
            lines.append(f"- {status} {input_text}...")
        return "\n".join(lines)


# 全局实例缓存
_nurture_cache = {}

def get_nurture(user_id: str = "default") -> LLMNurture:
    if user_id not in _nurture_cache:
        _nurture_cache[user_id] = LLMNurture(user_id)
    return _nurture_cache[user_id]
