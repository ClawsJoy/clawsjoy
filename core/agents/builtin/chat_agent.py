"""对话 Agent - 自然语言对话"""

from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent
from core.lib.smart_adapter import smart_adapter


class ChatAgent(SmartAgent):
    name = "chat_agent"
    description = "通用聊天助手"
    version = "2.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._load_agent_config()
        print("💬 对话Agent 初始化完成")

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        print(f"[对话] 收到: {user_input}")
        
        result = smart_adapter.generate(
            user_input,
            model=self.llm_model,
            temperature=self.llm_temperature
        )
        
        return {
            "success": True,
            "response": result,
            "agent": self.name,
            "user_id": self.user_id
        }
