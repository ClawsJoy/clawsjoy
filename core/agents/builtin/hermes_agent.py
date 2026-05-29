"""Hermes 智能 Agent"""

from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent
from core.lib.smart_adapter import smart_adapter


class HermesAgent(SmartAgent):
        import requests
    name = "hermes_agent"
    description = "Hermes智能体"
    type = "core"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"🧠 HermesAgent 初始化完成")

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        prompt = f"作为智能助手，请处理以下任务：{user_input}"
        response = smart_adapter.generate(prompt, auto_select=True)
        return {
            "success": True,
            "response": response,
            "agent": self.name,
            "user_id": self.user_id
        }


hermes_agent = HermesAgent()
