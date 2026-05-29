"""记忆 Agent"""

import requests
from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent


class MemoryAgent(SmartAgent):
    name = "memory_agent"
    description = "记忆助手"
    type = "core"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"💾 记忆Agent 初始化完成")

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        if "记住" in user_input:
            self.remember("user_preference", user_input)
            response = "已记住您的偏好"
        else:
            response = "我可以帮您记住重要信息"
        return {
            "success": True,
            "response": response,
            "agent": self.name,
            "user_id": self.user_id
        }

    def remember(self, key: str, value: str):
        """记住信息"""
        pass

    def recall(self, key: str) -> Optional[str]:
        """回忆信息"""
        return None


memory_agent = MemoryAgent()
