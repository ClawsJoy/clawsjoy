#!/usr/bin/env python3
"""Layered - Layered 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class MemoryItem:
    """记忆项"""
    content: str
    type: str  # conversation, preference, fact, todo
    importance: int  # 1-10
    timestamp: float
    metadata: Dict = field(default_factory=dict)


class LayeredMemory:
    """L0-L4 分层记忆管理器"""
    
    def __init__(self, user_id: str, agent_name: str):
        self.user_id = user_id
        self.agent_name = agent_name
        self.base_path = Path(f"{config_helper.get_data_root()}/v5/users/{user_id}/layered_memory/{agent_name}")
        self.base_path.mkdir(parents=True, exist_ok=True)

        # L0: 会话记忆（短期）
        self.l0_session: List[MemoryItem] = []

        # L1: 日记忆（中期）
        self.l1_daily: List[MemoryItem] = []

        # L2: 长期记忆
        self.l2_long: List[MemoryItem] = []

        # L3: 向量记忆（语义）
        self.l3_vector: List[Dict] = []

        # L4: 索引记忆（知识图谱）
        self.l4_index: Dict[str, List[str]] = {}

        self._load()
    
    def _get_file(self, level: str) -> Path:
        return self.base_path / f"l{level}.json"
    
    def _load(self):
        """加载所有层级记忆"""
        for level in ['0', '1', '2', '3', '4']:
            file_path = self._get_file(level)
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if level == '0':
                            self.l0_session = [MemoryItem(**item) for item in data]
                        elif level == '1':
                            self.l1_daily = [MemoryItem(**item) for item in data]
                        elif level == '2':
                            self.l2_long = [MemoryItem(**item) for item in data]
                        elif level == '3':
                            self.l3_vector = data
                        elif level == '4':
                            self.l4_index = data
                except:
                    pass
    
    def _save(self, level: str):
        """保存指定层级"""
        file_path = self._get_file(level)
        if level == '0':
            data = [{'content': m.content, 'type': m.type, 'importance': m.importance, 
                     'timestamp': m.timestamp, 'metadata': m.metadata} for m in self.l0_session]
        elif level == '1':
            data = [{'content': m.content, 'type': m.type, 'importance': m.importance,
                     'timestamp': m.timestamp, 'metadata': m.metadata} for m in self.l1_daily]
        elif level == '2':
            data = [{'content': m.content, 'type': m.type, 'importance': m.importance,
                     'timestamp': m.timestamp, 'metadata': m.metadata} for m in self.l2_long]
        elif level == '3':
            data = self.l3_vector
        elif level == '4':
            data = self.l4_index
        else:
            return

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add(self, content: str, mem_type: str = "conversation", importance: int = 5):
        """添加记忆（自动分层）"""
        item = MemoryItem(
            content=content[:500],
            type=mem_type,
            importance=importance,
            timestamp=time.time()
        )

        # L0: 会话记忆
        self.l0_session.append(item)
        self._save('0')

        # 自动压缩
        self._compress()
    
    def _compress(self):
        """自动压缩记忆"""
        # L0 → L1 压缩
        if len(self.l0_session) > 50:
            # 提取重要记忆
            important = [m for m in self.l0_session if m.importance >= 4]
            self.l1_daily.extend(important)
            self.l0_session = self.l0_session[-20:]
            self._save('0')
            self._save('1')

        # L1 → L2 压缩
        if len(self.l1_daily) > 100:
            important = [m for m in self.l1_daily if m.importance >= 6]
            self.l2_long.extend(important)
            self.l1_daily = self.l1_daily[-50:]
            self._save('1')
            self._save('2')

        # L2 限制
        if len(self.l2_long) > 500:
            self.l2_long = self.l2_long[-500:]
            self._save('2')
    
    def search(self, query: str, limit: int = 5) -> List[str]:
        """搜索记忆（优先 L2 → L1 → L0）"""
        results = []
        query_lower = query.lower()

        # 先搜索长期记忆
        for mem in reversed(self.l2_long):
            if query_lower in mem.content.lower():
                results.append(mem.content[:200])
                if len(results) >= limit:
                    return results

        # 再搜索日记忆
        for mem in reversed(self.l1_daily):
            if query_lower in mem.content.lower():
                results.append(mem.content[:200])
                if len(results) >= limit:
                    return results

        # 最后搜索会话记忆
        for mem in reversed(self.l0_session):
            if query_lower in mem.content.lower():
                results.append(mem.content[:200])
                if len(results) >= limit:
                    return results

        return results
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "l0_session": len(self.l0_session),
            "l1_daily": len(self.l1_daily),
            "l2_long": len(self.l2_long),
            "l3_vector": len(self.l3_vector),
            "l4_index": len(self.l4_index)
        }
