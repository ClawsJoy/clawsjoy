"""统一对话引擎 - 修复版"""

import requests
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class UnifiedChatEngine:
    def __init__(self):
        self.enabled = True
        self.llm_url = "http://localhost:5012/chat"

    def execute(self, message: str, user_id: str = "guest") -> Dict:
        """直接调用 LLM，不使用缓存"""
        import requests

        try:
            resp = requests.post(
                self.llm_url,
                json={"message": message},
                timeout=60,
                headers={"Content-Type": "application/json"}
            )
            if resp.status_code == 200:
                result = resp.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "agent": "chat_engine",
                    "user_id": user_id
                }
            else:
                return {
                    "success": False,
                    "response": f"服务错误: {resp.status_code}",
                    "agent": "error",
                    "user_id": user_id
                }
        except Exception as e:
            return {
                "success": False,
                "response": f"服务异常: {str(e)}",
                "agent": "error",
                "user_id": user_id
            }


chat_engine = UnifiedChatEngine()
