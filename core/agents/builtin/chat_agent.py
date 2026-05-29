"""聊天智能体 - 继承 SmartAgent 获得高级能力"""

from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent


class ChatAgent(SmartAgent):
    """聊天智能体 - 继承智能体基类"""

    name = "chat_agent"
    description = "通用聊天助手"
    type = "core"
    version = "2.0.0"

    def __init__(self, user_id: str = "guest"):
        super().__init__(user_id=user_id)
        self._load_chat_config()

    def _load_chat_config(self):
        """加载聊天配置"""
        import yaml
        from pathlib import Path
        config_file = Path("config/agents/chat.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.chat_config = yaml.safe_load(f)

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理用户输入"""
        # 直接返回响应，不调用父类
        return {
            "success": True,
            "response": f"收到消息: {user_input}",
            "agent": self.name,
            "user_id": self.user_id
        }


# chat_agent = ChatAgent()  # 注释：改为按需创建
