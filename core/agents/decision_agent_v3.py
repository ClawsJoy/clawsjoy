import sys; sys.path.insert(0, "/mnt/d/clawsjoy_clean")
#!/usr/bin/env python3
"""决策 Agent v3 - 集成参数采集"""

import time
from typing import Dict, Any, Optional

from agents.base_agent import BaseAgent
from lib.file_exchange import file_exchange
from agents.collector_agent import collector_agent


class DecisionAgent(BaseAgent):
    """决策 Agent - 用户总管（带参数采集）"""
    
    def __init__(self):
        super().__init__("DecisionAgent")
        self.sessions = {}
        self._running = False
        self.log("决策 Agent v3 初始化完成")
    
    def process(self, user_input: str) -> Dict[str, Any]:
        """处理用户请求"""
        self.log(f"收到请求: {user_input[:50]}...")
        
        session_id = f"session_{int(time.time())}"
        
        # 识别技能（简化：关键词匹配）
        skill = "ai-image-gen"
        if "调度" in user_input or "定时" in user_input:
            skill = "scheduler"
        
        # 开始采集会话
        next_q = collector_agent.start_session(session_id, skill, "default_user")
        
        self.sessions[session_id] = {
            "user_input": user_input,
            "skill": skill,
            "status": "collecting"
        }
        
        # 生成话术
        if next_q:
            message = next_q["question"]
        else:
            message = "好的，正在处理..."
        
        # 发送给聊天 Agent 生成话术
        file_exchange.send(
            to_agent="chat",
            data={
                "from": "decision",
                "action": "generate_response",
                "data": {
                    "user_input": user_input,
                    "session_id": session_id,
                    "suggested_response": message
                }
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
        
        if action == "user_response":
            # 用户回复
            session_id = data.get("session_id")
            user_reply = data.get("user_reply", "")
            
            # 更新采集 Agent
            # 这里需要解析用户回复，简化为直接使用
            result = collector_agent.update(session_id, "subject", user_reply)
            
            if result.get("status") == "complete":
                # 采集完成，执行技能
                collected = collector_agent.get_collected(session_id)
                self._execute_task(session_id, collected)
            else:
                # 继续采集
                next_q = result.get("next_question")
                file_exchange.send(
                    to_agent="chat",
                    data={
                        "from": "decision",
                        "action": "generate_response",
                        "data": {
                            "session_id": session_id,
                            "suggested_response": next_q
                        }
                    }
                )
        
        elif action == "response_ready":
            # 聊天 Agent 的话术已生成，直接转发给用户（这里简化为日志）
            session_id = data.get("session_id")
            response = data.get("response")
            self.log(f"回复用户 [{session_id}]: {response}")
    
    def _execute_task(self, session_id: str, params: Dict):
        """执行任务"""
        self.log(f"执行任务: {session_id}, 参数: {params}")
        
        # 构建 prompt
        prompt = f"{params.get('subject', '')}，{params.get('age', '')}，{params.get('expression', '')}，{params.get('style', '')}风格"
        
        file_exchange.send(
            to_agent="executor",
            data={
                "from": "decision",
                "action": "execute",
                "data": {
                    "task_id": session_id,
                    "skill": "ai-image-gen",
                    "params": {"prompt": prompt}
                }
            }
        )
    
    def stop(self):
        self._running = False


decision_agent = DecisionAgent()


if __name__ == "__main__":
    print("决策 Agent v3 测试")
    result = decision_agent.process("我想要漫剧人物")
    print(f"结果: {result}")
