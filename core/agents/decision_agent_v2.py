#!/usr/bin/env python3
"""决策 Agent v2 - 完整的消息处理"""

import time
from typing import Dict, Any, Optional

from core.agent.base import BaseAgent
from lib.file_exchange import file_exchange


class DecisionAgent(BaseAgent):
    """决策 Agent - 用户总管"""
    
    def __init__(self):
        super().__init__("DecisionAgent")
        self.sessions = {}
        self._running = False
        self.log("决策 Agent 初始化完成")
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理用户请求"""
        self.log(f"收到请求: {user_input[:50]}...")
        
        session_id = f"session_{int(time.time())}"
        self.sessions[session_id] = {
            "user_input": user_input,
            "status": "waiting_chat",
            "collected": {}
        }
        
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
            message = file_exchange.receive("decision")
            if message:
                self._handle_message(message)
            time.sleep(0.5)
    
    def _handle_message(self, message: Dict):
        action = message.get("action")
        data = message.get("data", {})
        from_agent = message.get("from")
        
        self.log(f"收到消息: {action} from {from_agent}")
        
        if action == "response_ready":
            session_id = data.get("session_id")
            user_input = data.get("user_input")
            
            if session_id in self.sessions:
                self.sessions[session_id]["status"] = "ready_to_execute"
            
            file_exchange.send(
                to_agent="executor",
                data={
                    "from": "decision",
                    "action": "execute",
                    "data": {
                        "task_id": session_id,
                        "skill": "ai-image-gen",
                        "params": {"prompt": user_input}
                    }
                }
            )
            self.log(f"已转发到执行 Agent: {session_id}")
        
        elif action == "task_complete":
            session_id = data.get("task_id")
            result = data.get("result")
            
            if session_id in self.sessions:
                self.sessions[session_id]["status"] = "completed"
                self.sessions[session_id]["result"] = result
            
            self.log(f"任务完成: {session_id}")
    
    def stop(self):
        self._running = False


decision_agent = DecisionAgent()


if __name__ == "__main__":
    print("决策 Agent v2 测试")
    result = decision_agent.process("我想要漫剧人物")
    print(f"结果: {result}")
