#!/usr/bin/env python3
"""Communication Mixin - Communication Mixin 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""


from core.lib.agent_bus import get_bus


class CommunicationMixin:
    """通信混入 - 提供发布/订阅能力"""

    def init_communication(self, agent_name: str):
        """初始化通信"""
        self.bus = get_bus()
        self.agent_name = agent_name
        if self.bus:
            self.bus.subscribe(agent_name, "agent.response")
            self.bus.subscribe(agent_name, "agent.error")
        print(f"📡 [{agent_name}] 通信已初始化")

    def publish(self, topic: str, content: dict, priority: int = 0):
        """发布消息"""
        if hasattr(self, "bus") and self.bus:
            return self.bus.publish(self.agent_name, topic, content, priority)
        return None

    def subscribe(self, topic: str):
        """订阅主题"""
        if hasattr(self, "bus") and self.bus:
            self.bus.subscribe(self.agent_name, topic)

    def register_handler(self, topic: str, handler):
        """注册消息处理器"""
        if hasattr(self, "bus") and self.bus:
            self.bus.register_handler(topic, handler)
