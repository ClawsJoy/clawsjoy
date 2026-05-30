#!/usr/bin/env python3
"""Manager - Manager 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class MemoryManager:
    """记忆管理器"""
    
    def __init__(self, user_id: str, agent_name: str):
        self.user_id = user_id
        self.agent_name = agent_name
        self.base_path = Path(f"{config_helper.get_data_root()}/v5/users/{user_id}/memory/{agent_name}")
        self.base_path.mkdir(parents=True, exist_ok=True)

        # 加载数据
        self.preferences = self._load("preferences.json")
        self.history = self._load("history.json")
        self.knowledge = self._load("knowledge.json")

        if not isinstance(self.history, list):
            self.history = []
    
    def _load(self, filename: str) -> Any:
        """加载数据"""
        file_path = self.base_path / filename
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {} if "preferences" in filename or "knowledge" in filename else []
    
    def _save(self, filename: str, data: Any):
        """保存数据"""
        with open(self.base_path / filename, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def remember(self, key: str, value: Any):
        """记住偏好"""
        self.preferences[key] = value
        self._save("preferences.json", self.preferences)
    
    def recall(self, key: str) -> Any:
        """回忆偏好"""
        return self.preferences.get(key)
    
    def add_history(self, user_msg: str, assistant_msg: str):
        """添加历史记录"""
        entry = {
            "user": user_msg,
            "assistant": assistant_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.history.append(entry)
        # 保留最近100条
        if len(self.history) > 100:
            self.history = self.history[-100:]
        self._save("history.json", self.history)
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """获取历史记录"""
        return self.history[-limit:]
    
    def remember_knowledge(self, key: str, value: Any):
        """记住知识"""
        self.knowledge[key] = value
        self._save("knowledge.json", self.knowledge)
    
    def recall_knowledge(self, key: str) -> Any:
        """回忆知识"""
        return self.knowledge.get(key)
    
    def search_context(self, query: str, limit: int = 5) -> List[str]:
        """搜索相关上下文"""
        results = []
        query_lower = query.lower()
        for h in reversed(self.history):
            if query_lower in h.get("user", "").lower() or query_lower in h.get("assistant", "").lower():
                results.append(f"用户: {h['user'][:100]}\n助手: {h['assistant'][:100]}")
                if len(results) >= limit:
                    break
        return results
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "preferences": len(self.preferences),
            "history": len(self.history),
            "knowledge": len(self.knowledge)
        }
