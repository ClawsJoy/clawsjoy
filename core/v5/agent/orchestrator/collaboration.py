#!/usr/bin/env python3
"""Collaboration - Collaboration 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List


@dataclass
class Message:
    """Agent 间消息"""

    id: str
    from_agent: str
    to_agent: str
    content: str
    type: str  # request, response, broadcast
    timestamp: str


class CollaborationHub:
    """协作中心 - 管理 Agent 间通信"""

    def __init__(self):
        self.agents: Dict[str, Callable] = {}
        self.message_queue: List[Message] = []
        self.subscribers: Dict[str, List[Callable]] = {}

    def register_agent(self, name: str, handler: Callable):
        """注册 Agent"""
        self.agents[name] = handler
        print(f"   ✅ Agent 已注册: {name}")

    def send(self, from_agent: str, to_agent: str, content: str) -> bool:
        """发送消息"""
        if to_agent not in self.agents:
            return False

        msg = Message(
            id=str(uuid.uuid4())[:8],
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            type="request",
            timestamp=datetime.now().isoformat(),
        )

        self.message_queue.append(msg)

        # 尝试立即处理
        try:
            handler = self.agents[to_agent]
            response = handler(content)
            return True
        except Exception as e:
            return False

    def broadcast(self, from_agent: str, content: str):
        """广播消息"""
        for agent_name in self.agents:
            if agent_name != from_agent:
                self.send(from_agent, agent_name, content)

    def get_messages(self, agent_name: str, limit: int = 10) -> List[Message]:
        """获取发给某 Agent 的消息"""
        return [m for m in self.message_queue if m.to_agent == agent_name][-limit:]


# 全局协作中心
collaboration = CollaborationHub()
