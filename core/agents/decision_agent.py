#!/usr/bin/env python3
"""决策 Agent - 用户总管"""

import time
import json
from pathlib import Path
from typing import Dict, Any, Optional

from core.agent.base import BaseAgent
from lib.file_exchange import file_exchange


class DecisionAgent(BaseAgent):
    """决策 Agent - 负责调度和决策"""
    
    def __init__(self):
        super().__init__("DecisionAgent")
        self.sessions = {}
        self.user_preferences = {}
        self._running = False
        self.log("决策 Agent 初始化完成")
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理用户请求"""
        self.log(f"收到请求: {user_input[:50]}...")
        
        session_id = f"session_{int(time.time())}"
        self.sessions[session_id] = {
            "user_input": user_input,
            "status": "processing"
        }
        
        # 发送给聊天 Agent
        file_exchange.send(
            to_agent="chat",
            data={
                "from": "decision",
                "action": "generate_response",
                "data": {"user_input": user_input, "session_id": session_id}
            }
        )
        
        return {"success": True, "session_id": session_id}
    
    def run(self):
        """运行主循环"""
        self._running = True
        self.log("决策 Agent 启动，等待消息...")
        
        while self._running:
            msg = file_exchange.receive("decision")
            if msg:
                self.log(f"收到消息: {msg.get('action')}")
            time.sleep(0.5)
    
    def stop(self):
        self._running = False


decision_agent = DecisionAgent()


if __name__ == "__main__":
    result = decision_agent.process("我想要漫剧人物")
    print(f"结果: {result}")
